from psychopy import prefs
#change the pref libraty to PTB and set the latency mode to high precision
prefs.hardware['audioLib'] = 'PTB'
prefs.hardware['audioLatencyMode'] = 3

import os
from time import time, strftime, gmtime
from glob import glob
from random import choice
from optparse import OptionParser
import random

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG
from eegnb.stimuli import Famous_Nonfamous

__title__ = "Celebrity N170"


def present(duration=120, eeg: EEG=None, save_fn=None, subject=0, session=0,
            n_trials = 30, iti = 1, soa = 0.450, jitter = 0.150):
    
    record_duration = np.float32(duration)
    markernames = [1, 2]

    
    # Setup trial list
    image_type = np.random.binomial(1, 0.5, n_trials)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # start the EEG stream, will delay 5 seconds to let signal settle
  
    # create a timer for the experiment and EEG markers
    clock = core.Clock()
    start = time()
    
    # Setup graphics
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)

    famous = list(map(load_image, glob(os.path.join(Famous_Nonfamous, "famous", "*.jpg"))))
    print('yay')
    nonfamous = list(map(load_image, glob(os.path.join(Famous_Nonfamous, "nonfamous", "*.jpg"))))
    print('yay2')
    stim = [famous, nonfamous]
    
    fixation = visual.GratingStim(win=mywin, size=0.2, pos=[0, 0], sf=0)
    
    # Set up response array: saving trial information for output
    responses = []
    
    # Show the instructions screen
    show_instructions(duration)

    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            random_id = random.randint(1000,10000)
            random_ses = random.randint(1000,10000)
            save_fn = generate_save_fn(eeg.device_name, "celebrity_n170", random_id, random_ses, "unnamed")
            print(
                f"No path for a save file was passed to the experiment. Saving data to {save_fn}"
            )
        eeg.start(save_fn, duration=record_duration + 5)

    # Start EEG Stream, wait for signal to settle, and then pull timestamp for start point
    start = time()

    # Iterate through the events
    for ii, trial in trials.iterrows():
        
        # Select and display image
        label = trials["image_type"].iloc[ii]
        image = choice(famous if label == 1 else nonfamous)
        image.draw()
        
        # trial begins here: intertrial interval
        core.wait(iti + np.random.rand() * jitter)

        # Push sample
        if eeg:
            timestamp = time()
            if eeg.backend == "muselsl":
                marker = [markernames[label]]
            else:
                marker = markernames[label]
            eeg.push_sample(marker=marker, timestamp=timestamp)

        mywin.flip()

        # Stimulus offset / response begin
        core.wait(soa)
        fixation.draw()
        t_respOnset = clock.getTime() # sets time for when response period began
        mywin.flip()
        
        # wait until response + resp offset
        keys = event.waitKeys(keyList=["f", "j"], timeStamped=clock) # locked to same clock as response
        
        correct = 0
        response = 0
        
        # classify response as correct / incorrect
        if keys[0][0] == "f":
            response = 1 # pressed "know" key
            if label == 1:
                correct = 1
            else:
                correct = 2
        elif keys[0][0] == "j":
            response = 2 # pressed "unknown" key
            if label == 2:
                correct = 2
            else:
                correct = 1
        else:
            response = 0
            correct = 0
        
        # save trial info into array
        tempArray = [ii + 1, label, response, correct]
        responses.append(tempArray)
        column_labels = [
            "trial",
            "target type",
            "response",
            "accuracy",
        ]
        
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break

        event.clearEvents()
    
    # write behavioural output file
    directory = os.path.join(
        os.path.expanduser("~"),
        ".eegnb",
        "data",
        "celebrity-N170",
        "behaviour",
        "subject" + str(subject),
        "session" + str(session),
    )
    if not os.path.exists(directory):
        os.makedirs(directory)
    outname = os.path.join(
        directory,
        "subject"
        + str(subject)
        + "_session"
        + str(session)
        + ("_behOutput_%s.csv" % strftime("%Y-%m-%d-%H.%M.%S", gmtime())),
    )
    output = DataFrame(responses)
    output.to_csv(path_or_buf = outname, header = column_labels)
    
    # Cleanup
    if eeg:
        eeg.stop()

    mywin.close()


def show_instructions(duration):

    instruction_text = """
    Welcome to the Celebrity N170 experiment! 
 
    Stay still, focus on the centre of the screen, and try not to blink. 
    
    After each picture, press F if you recognized the face, and J if you did not. Please respond as quickly and accurately as possible.

    This block will run for %s seconds.

    Press spacebar to continue. 
    
    """
    instruction_text = instruction_text % duration

    # graphics
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)

    mywin.mouseVisible = False

    # Instructions
    text = visual.TextStim(win=mywin, text=instruction_text, color=[-1, -1, -1])
    text.draw()
    mywin.flip()
    event.waitKeys(keyList="space")

    mywin.mouseVisible = True
    mywin.close()

from psychopy import prefs
#change the pref libraty to PTB and set the latency mode to high precision
prefs.hardware['audioLib'] = 'PTB'
prefs.hardware['audioLatencyMode'] = 3

import os
from time import time
from glob import glob
from random import choice, shuffle
from optparse import OptionParser
import random

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG
from eegnb.stimuli import MEN_WOMEN

__title__ = "Color Knowledge Practice"

# current problems
    # we need to input the behavioral task aspect of our experiment
        # how would you rate the coloring of the object? 
            # need to figure out timing aspects for this as well
    # we need to smooth out all of the image conditions due to our different sets of stimuli

def present(duration=60, eeg: EEG=None, save_fn=None,
            n_trials = 6, iti = 0.5, soa = 1, jitter = 0.2, subject=0, session=0):
    
    record_duration = np.float32(duration)
    markernames = [1, 2, 3]

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # start the EEG stream, will delay 5 seconds to let signal settle

    # Setup graphics
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
  
    congruent = list(map(load_image, glob(os.path.join(PRACTICE_COLORS_OBJECTS, "congruent", "*_1.png"))))
    incongruent = list(map(load_image, glob(os.path.join(PRACTICE_COLORS_OBJECTS, "incongruent", "*_2.png"))))
    shuffle(congruent)
    shuffle(incongruent)
    stim = [congruent, incongruent]
    
    # Setup trial list
    # image_type = np.random.binomial(1, 0.5, n_trials)
    image_type = np.zeros(len(congruent))
    image_type = np.append(image_type, np.full(len(incongruent), 1))
    shuffle(image_type)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    # Show the instructions screen
    show_instructions()

    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            random_id = random.randint(1000,10000)
            save_fn = generate_save_fn(eeg.device_name, "color_knowledge", random_id, random_id, "unnamed")
            print(
                f"No path for a save file was passed to the experiment. Saving data to {save_fn}"
            )
        eeg.start(save_fn, duration=record_duration + 5)

    # create a clock for rt's
    clock = core.Clock()
        
    # Start EEG Stream, wait for signal to settle, and then pull timestamp for start point
    start = time()
    
    # Set up response array: saving trial information for output
    responses = []
    
    # Set up list index counters
    cong_idx = 0
    incong_idx = 0

    # Iterate through the events
    for ii, trial in trials.iterrows():
        # Inter trial interval
        core.wait(iti + np.random.rand() * jitter)

        label = trials["image_type"].iloc[ii]
        if label == 0:
            image = congruent[cong_idx]
            cong_idx += 1
        elif label == 1:
            image = incongruent[incong_idx]
            incong_idx += 1
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
        
        t_respOnset = clock.getTime() # sets time for when response period began
        keys = []
        keys = event.waitKeys(maxWait=2, keyList=["1", "2"], timeStamped=clock) # locked to same clock as response
        
        # Stimulus offset / response begin
        #core.wait(soa)
        
        # wait until response + resp offset
        mywin.flip()
        
        correct = 0
        response = 0
        
        # classify response as correct / incorrect
        if keys[0][0] == "1":
            response = 1 # pressed congruent key
            if label == 0:
                correct = 1
            else:
                correct = 0
        elif keys[0][0] == "2":
            response = 2 # pressed incongruent key
            if label == 0:
                correct = 0
            else:
                correct = 1
        else:
            pass
        
        # save trial info into array
        tempArray = [ii + 1, label + 1, response, correct]
        responses.append(tempArray)
        column_labels = [
            "trial",
            "target type",
            "response",
            "accuracy"
        ]
        
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break

        event.clearEvents()
    
    # write behaviural output file
    directory = os.path.join(
        os.path.expanduser("~"),
        ".eegnb",
        "data",
        "color_knowledge",
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
        + "_behOutput.csv",
    )
    output = DataFrame(responses)
    output.to_csv(path_or_buf = outname, header = column_labels)
    
    # Cleanup
    if eeg:
        eeg.stop()

    mywin.close()


def show_instructions():
  
    # change "side keyboard" portion and numbering depending on what we are able to figure out
    instruction_text = """
    Welcome to the color knowledge experiment practice! 
    
    Your task is to view the presented objects. When the "?" screen appears, rate the items on the side keyboard according to the below criteria:
    
    1 = congruent (like you see everyday), 2 = incongruent (abnormally colored), 3 = achromatic (black and white)
    
    You will have two seconds to make your rating before the next image appears. 
 
    Stay still, focus on the center of the screen, and refrain from blinking. Let the experimenters know now if you have any questions.

    Press SPACEBAR to continue. 
    
    """

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
    
    
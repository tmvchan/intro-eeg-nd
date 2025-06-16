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
from eegnb.stimuli import COLORS_OBJECTS

__title__ = "Color Knowledge Session"

def present(duration=200, eeg: EEG=None, save_fn=None,
            n_trials = 78, iti = 0.5, soa = 1, jitter = 0.2, subject=0, session=0):
    
    record_duration = np.float32(duration)
    markernames = [1, 2, 3]

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # start the EEG stream, will delay 5 seconds to let signal settle

    # Setup graphics
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
  
    congruent = list(map(load_image, glob(os.path.join(COLORS_OBJECTS, "congruent", "*_1.png"))))
    incongruent = list(map(load_image, glob(os.path.join(COLORS_OBJECTS, "incongruent", "*_2.png"))))
    achromatic = list(map(load_image, glob(os.path.join(COLORS_OBJECTS, "achromatic", "*_3.png"))))
    shuffle(congruent)
    shuffle(incongruent)
    shuffle(achromatic)
    stim = [congruent, incongruent, achromatic]
    
    # Setup trial list
    # image_type = np.random.binomial(1, 0.5, n_trials)
    image_type = np.zeros(len(congruent))
    image_type = np.append(image_type, np.full(len(incongruent), 1))
    image_type = np.append(image_type, np.full(len(achromatic), 2))
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
    achr_idx = 0

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
        elif label == 2:
            image = achromatic[achr_idx]
            achr_idx += 1
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
        
        keys = event.waitKeys(maxWait=2, keyList=["1", "2", "3"], timeStamped=clock) # locked to same clock as response
        
        # Stimulus offset / response begin
        #core.wait(soa)
        
        # wait until response + resp offset
        mywin.flip()
        
        correct = 0
        response = 0
        
        # classify response as correct / incorrect
        if not keys:
            pass
        elif keys[0][0] == "1":
            response = 1 # pressed congruent key
            if label == 1:
                correct = 0
            if label == 2: 
                correct = 0
            else:
                correct = 1
        elif keys[0][0] == "2":
            response = 2 # pressed incongruent key
            if label == 0:
                correct = 0
            if label == 2: 
                correct = 0
            else: 
                correct = 1
        elif keys[0][0] == "3": 
            response = 3 # pressed achromatic key
            if label == 0:
                correct = 0
            if label == 1:
                correct = 0
            else:
                correct = 1
        
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
    
    # write behavioral output file
    directory = os.path.join(
        os.path.expanduser("~"),
        ".eegnb",
        "data",
        "color_knowledge",
        "session_behavior",
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
  
    instruction_text = """
    Welcome back to the experiment! 
    
    During these trials, you will once again view objects and be asked to rate them according to their color condition. 
    
    1 = congruent, 2 = incongruent, 3 = achromatic
 
    Stay still, focus on the center of the screen, and refrain from blinking.
    
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
     
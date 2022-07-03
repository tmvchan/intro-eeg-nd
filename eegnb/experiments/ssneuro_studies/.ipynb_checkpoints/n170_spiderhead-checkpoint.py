from psychopy import prefs
#change the pref libraty to PTB and set the latency mode to high precision
prefs.hardware['audioLib'] = 'PTB'
prefs.hardware['audioLatencyMode'] = 3

import os
from time import time
from glob import glob
from random import choice
from optparse import OptionParser
import random

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG
from eegnb.stimuli import RED_CIRCLE

from PIL import Image
# im = Image.open("red_circle.png")

__title__ = "Spiderhead 2.0"



def present(duration=150, eeg: EEG=None, save_fn=None, subject=0, session=0,
            n_trials = 30, iti = random.choice([1.4, 2, 2.75]), soa = 0.3, jitter = 0.4):
    
    record_duration = np.float32(duration)
    markernames = [1, 2]

    # Setup trial list
    image_type = np.full(n_trials, 1, dtype=int)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # start the EEG stream, will delay 5 seconds to let signal settle

    # Setup graphics
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)

    RedCirc = list(map(load_image, glob(os.path.join(RED_CIRCLE, "*.png"))))
    stim = RedCirc
    clock = core.Clock()
    responses = []

    # Show the instructions screen
    show_instructions()

    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            random_id = random.randint(1000,10000)
            save_fn = generate_save_fn(eeg.device_name, "visual_n170", random_id, random_id, "unnamed")
            print(
                f"No path for a save file was passed to the experiment. Saving data to {save_fn}"
            )
        eeg.start(save_fn, duration=record_duration + 5)

    # Start EEG Stream, wait for signal to settle, and then pull timestamp for start point
    start = time()

    # Iterate through the events
    for ii, trial in trials.iterrows():
        
        # Inter trial interval
        core.wait(iti + np.random.rand() * jitter)
        
        # Select and display image
        label = trials["image_type"].iloc[ii]
        image = choice(RedCirc)
        image.draw()

        # Push sample
        if eeg:
            timestamp = time()
            if eeg.backend == "muselsl":
                marker = [markernames[label]]
            else:
                marker = markernames[label]
            eeg.push_sample(marker=marker, timestamp=timestamp)

        mywin.flip()

        # measure response
        respstart = clock.getTime()

        # get response
        keys = event.waitKeys(maxWait = 5, keyList = ["space"], timeStamped = clock)
        
        # offset
        core.wait(soa)
        mywin.flip()
        
        # reaction time calculation
        rt = keys[0][1] - respstart 
        # save RT
        tempArray = [ii + 1, rt  *1000]
        responses.append(tempArray)

        #if len(event.getKeys()) > 0 or (time() - start) > record_duration:
        if (time() - start) > record_duration:
            break

        event.clearEvents()

    directory = os.path.join(
        os.path.expanduser("~"),
        ".eegnb",
        "data",
        "circleRT",
        "subject" + str(subject),
        "session" + str(session)
    )

    if not os.path.exists(directory):
        os.makedirs(directory)

    outname = os.path.join(
        directory,
        "subject" + str(subject) + "_session" + str(session) + "_RT.csv"
    )

    output = np.array(responses)
    np.savetxt(outname, output, delimiter=",")

    # Cleanup
    if eeg:
        eeg.stop()

    mywin.close()


def show_instructions():

    instruction_text = """
    Welcome to the Spiderhead 2.0 experiment! 

    When you see a RED CIRCLE appear on your screen press the SPACEBAR as quickly as possible.

    Stay still, move only your finger, and try not to blink. 

    Press SPACEBAR to continue. 
    
    """
    # instruction_text = instruction_text % duration

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

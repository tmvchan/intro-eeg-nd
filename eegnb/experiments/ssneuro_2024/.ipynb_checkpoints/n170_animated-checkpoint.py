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
from eegnb.stimuli import HUMAN_ANIMAL

__title__ = "Visual N170 with Animals and Animateds"


def present(duration=120, eeg: EEG=None, save_fn=None,
            n_trials = 2010, iti = 1, soa = 2, jitter = 0.2):
    
    record_duration = np.float32(duration)
    markernames = [1, 2, 3, 4] # 1: human real, 2: human animated, 3: animal real, 4: animal animated

    # Setup trial list
    image_type = np.random.randint(0, 4, n_trials)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # start the EEG stream, will delay 5 seconds to let signal settle

    # Setup graphics
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)

    humans_real = list(map(load_image, glob(os.path.join(HUMAN_ANIMAL, "human", "real", "*.jpg"))))
    humans_anim = list(map(load_image, glob(os.path.join(HUMAN_ANIMAL, "human", "animated", "*.jpg"))))
    animals_real = list(map(load_image, glob(os.path.join(HUMAN_ANIMAL, "animals", "real", "*.jpg"))))
    animals_anim = list(map(load_image, glob(os.path.join(HUMAN_ANIMAL, "animals", "animated", "*.jpg"))))
    stim = [humans_real, humans_anim, animals_real, animals_anim]

    # Show the instructions screen
    show_instructions(duration)

    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            random_id = random.randint(1000,10000)
            save_fn = generate_save_fn(eeg.device_name, "n170_animated", random_id, random_id, "unnamed")
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
        image = choice(animals_anim if label == 3 else (animals_real if label == 2  else (humans_anim if label == 1 else humans_real)))
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

        # offset
        core.wait(soa)
        mywin.flip()
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break

        event.clearEvents()

    # Cleanup
    if eeg:
        eeg.stop()

    mywin.close()


def show_instructions(duration):

    instruction_text = """
    Welcome to the N170 experiment! 
 
    Stay still, focus on the centre of the screen, and try not to blink. 

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

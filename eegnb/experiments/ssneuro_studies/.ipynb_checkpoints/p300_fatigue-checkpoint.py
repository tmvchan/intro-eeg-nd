import os
from time import time
from glob import glob
from random import choice, shuffle

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from eegnb import generate_save_fn
from eegnb.stimuli import EASY_HARD

__title__ = "Mental Fatigue"


def present(duration=120, eeg=None, save_fn=None, ver=1):
    if ver is 1 or ver is 3: # easy
        n_trials = 15
    elif ver is 2: # hard
        n_trials = 30
    iti = 1
    soa = 4
    jitter = 0.5
    record_duration = np.float32(duration)
    markernames = [1, 2, 3]
    
    # Setup trial list
    image_type = np.full(n_trials, ver-1, dtype=int)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # Setup graphics
    mywin = visual.Window([1600, 900], color=[1,1,1], monitor="testMonitor", units="deg", fullscr=True)
    mywin.flip()
    mywin.flip()
    if ver is 1 or ver is 3:
        stim = list(map(load_image, glob(os.path.join(EASY_HARD, "easy-*.jpg"))))
    elif ver is 2:
        stim = list(map(load_image, glob(os.path.join(EASY_HARD, "hard-*.jpg"))))
   # stim = [targets]
    
    # so the words don't get loaded the same each time
    shuffle(stim)
    
    # go through list to make sure each one is picked once
    stim_list = []
    
    for ii, trial in trials.iterrows():
        
        # ensure that each file is picked once by indexing
        img_file = stim[ii]
        stim_list.append(img_file)
    
    # Show instructions
    show_instructions()

    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            save_fn = generate_save_fn(eeg.device_name, "mental_fatigue", "unnamed")
            print(
                f"No path for a save file was passed to the experiment. Saving data to {save_fn}"
            )
        eeg.start(save_fn, duration=record_duration)

    # Iterate through the events
    start = time()
    for ii, trial in trials.iterrows():
        # Inter trial interval
        core.wait(iti + np.random.rand() * jitter)

        # Select and display image
        label = trials["image_type"].iloc[ii]
        image = stim_list[ii]
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
    
    # Goodbye Screen
    text = visual.TextStim(
        win=mywin,
        text = "Thank you for participating. Press spacebar to exit the experiment.",
        color=[-1, -1, -1],
        pos=[0, 5],
    )
    text.draw()
    mywin.flip()
    event.waitKeys(keyList="space")

    mywin.mouseVisible = True
        
    # Cleanup
    if eeg:
        eeg.stop()
    mywin.close()


def show_instructions():
    
    instruction_text = """
    
    Try to mentally solve each question as it appears on the screen.

    Press spacebar to continue. 

    """
    #instruction_text = instruction_text % duration

    # graphics
    mywin = visual.Window([1600, 900], color=[1,1,1], monitor="testMonitor", units="deg", fullscr=True)
    mywin.mouseVisible = False
    mywin.flip()
    mywin.flip()
    
    # Instructions
    text = visual.TextStim(win=mywin, text=instruction_text, color=[-1, -1, -1])
    text.draw()
    mywin.flip()
    event.waitKeys(keyList="space")

    mywin.mouseVisible = True
    mywin.close()

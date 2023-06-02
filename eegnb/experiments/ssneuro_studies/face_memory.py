import os
from time import time
from glob import glob
from random import choice, shuffle

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from eegnb import generate_save_fn
from eegnb.stimuli import FACE_MEM

__title__ = "Memory for Faces"


def present(duration=120, eeg=None, save_fn=None, ver=1):
    n_trials = 30
    iti = 0.4
    soa = 1
    jitter = 0.1
    record_duration = np.float32(duration)
    markernames = [1, 2, 3, 4, 5, 6, 7, 8]
    
    # Setup trial list
    image_type = np.full(n_trials, ver-1, dtype=int)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # Setup graphics
    mywin = visual.Window([1600, 900], color=[1,1,1], monitor="testMonitor", units="deg", fullscr=True)
    mywin.flip()
    mywin.flip()
    if ver is 1:
        stim = list(map(load_image, glob(os.path.join(FACE_MEM, "face1*.jpeg"))))
    elif ver is 2:
        stim = list(map(load_image, glob(os.path.join(FACE_MEM, "face2*.jpeg"))))
    elif ver is 3:
        stim = list(map(load_image, glob(os.path.join(FACE_MEM, "face3*.jpeg"))))
    elif ver is 4:
        stim = list(map(load_image, glob(os.path.join(FACE_MEM, "face4*.jpeg"))))
    elif ver is 5:
        stim = list(map(load_image, glob(os.path.join(FACE_MEM, "face5*.jpeg"))))
    elif ver is 6:
        stim = list(map(load_image, glob(os.path.join(FACE_MEM, "face6*.jpeg"))))
    elif ver is 7:
        stim = list(map(load_image, glob(os.path.join(FACE_MEM, "face7*.jpeg"))))
    elif ver is 8:
        stim = list(map(load_image, glob(os.path.join(FACE_MEM, "face8*.jpeg"))))
    # stim = [targets]
    
    # Show instructions
    show_instructions()

    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            save_fn = generate_save_fn(eeg.device_name, "face_memory", "unnamed")
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
        image = choice(stim)
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
    
    Memorize this face that shows up on the screen.

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

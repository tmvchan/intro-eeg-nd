import os
from time import time
from glob import glob
from random import choice

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from eegnb import generate_save_fn
from eegnb.stimuli import EMOTIONS

__title__ = "Colour and Memory"


def present(duration=100, eeg=None, save_fn=None):
    iti = 3
    soa = 5
    jitter = 0.05
    record_duration = np.float32(duration)
    markernames = [1, 2, 3]
    n_trials = 5
   
    # Setup trial list
    image_type = np.random.randint(0, 3, n_trials)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # Setup graphics
    mywin = visual.Window([1600, 900], color=[1,1,1], monitor="testMonitor", units="deg", fullscr=True)
    mywin.flip()
    mywin.flip()

    positive = list(map(load_image, glob(os.path.join(EMOTIONS, "positive-*.png"))))
    bad = list(map(load_image, glob(os.path.join(EMOTIONS, "bad-*.png"))))
    neutral = list(map(load_image, glob(os.path.join(EMOTIONS, "neutral-*.png"))))

    stim = [positive, bad, neutral]

    # Show instructions
    show_instructions(duration=duration)

    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            save_fn = generate_save_fn(eeg.device_name, "visual_p300", "unnamed")
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
        image = choice(positive if label == 2  else (bad if label == 1 else neutral))
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


def show_instructions(duration):

    instruction_text = """
       
    Welcome to the P300 experiment!

    Stay still, focus on the centre of the screen, and try not to blink. Try to count the number of times a cat appears.

    This block will run for %s seconds.

    Press spacebar to continue.

    """
   
    instruction_text = instruction_text % duration

    # graphics
    mywin = visual.Window([1600, 900], color=[1,1,1], monitor="testMonitor", units="deg", fullscr=True)
    mywin.mouseVisible = False
    
    # Instructions
    text = visual.TextStim(win=mywin, text=instruction_text, color=[-1, -1, -1])
    text.draw()
    mywin.flip()
    event.waitKeys(keyList="space")

    mywin.mouseVisible = True
    mywin.close()
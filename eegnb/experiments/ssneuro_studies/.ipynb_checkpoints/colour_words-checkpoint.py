import os
from time import time
from glob import glob
from random import choice, sample

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from eegnb import generate_save_fn
from eegnb.stimuli import COLORS

__title__ = "Colour and Memory"


def present(duration=100, eeg=None, save_fn=None):
    iti = 3
    soa = 5
    jitter = 0.05
    record_duration = np.float32(duration)
    markernames = [1, 2, 3, 4, 5]
    n_trials = 25 # there are 25 words and they should be presented once per run. How many runs do you plan on doing? Having only five runs per colour is not optimal
   
    # Setup trial list
    type_list = [1 1 1 1 1 2 2 2 2 2 3 3 3 3 3 4 4 4 4 4 5 5 5 5 5]
    image_type = np.random.shuffle(type_list)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # Setup graphics
    mywin = visual.Window([1600, 900], color=[1,1,1], monitor="testMonitor", units="deg", fullscr=True)
    mywin.flip()
    mywin.flip()

    red = list(map(load_image, glob(os.path.join(COLORS, "red", "*.png"))))
    blue = list(map(load_image, glob(os.path.join(COLORS, "blue", "*.png"))))
    yellow = list(map(load_image, glob(os.path.join(COLORS, "yellow", "*.png"))))
    green = list(map(load_image, glob(os.path.join(COLORS, "green", "*.png"))))
    purple = list(map(load_image, glob(os.path.join(COLORS, "purple", "*.png"))))
    
    # so the words don't get loaded the same each time
    red = np.random.shuffle(red)
    blue = np.random.shuffle(blue)
    yellow = np.random.shuffle(yellow)
    green = np.random.shuffle(green)
    purple = np.random.shuffle(purple)
    
    # go through list to make sure each one is picked once
    stim_list = []
    for ii, trial in trials.iterrows():
        label = trials["image_type"].iloc[ii]
        img_file = sample(red if label == 0  else (blue if label == 1 else (yellow if label == 2 else (green if label == 3 else purple))), 1)[0]
        stim_list[ii] = img_file
        
        # remove from possibilities
        if label == 0:
            red.remove(img_file)
        elif label == 1: 
            blue.remove(img_file)
        elif label == 2:
            yellow.remove(img_file)
        elif label == 3: 
            green.remove(img_file)
        else:
            purple.remove(img_file)
    
    #stim = [red, blue, yellow, green, purple]

    # Show instructions
    show_instructions()

    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            save_fn = generate_save_fn(eeg.device_name, "color_words", "unnamed")
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
        # label = trials["image_type"].iloc[ii]
        # image = sample(red if label == 0  else (blue if label == 1 else (yellow if label == 2 else (green if label == 3 else purple))), 1)[0]
        image = stim_file[ii]
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
       
    Welcome to the experiment! 
    
    Please study and memorize the following words carefully. You will be asked to recall them later.
    
    Press the space bar to begin the experiment.

    """
   
    # instruction_text = instruction_text % duration

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
import os
from time import time
from glob import glob
from random import choice

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from eegnb import generate_save_fn
from eegnb.stimuli import COLORS_OBJECTS

__title__ = "Oddball task with color/odd colors stimuli"


def present(subject = 0, session = 0, duration=120, eeg=None, save_fn=None):
    iti = 0.4
    soa = 0.3
    jitter = 0.2
    n_trials = int(
        (duration - 3 - 2)
        / (iti + soa + jitter)
    )
    record_duration = np.float32(duration)
    markernames = [1, 2] # 1 = non-target, 2 = target
    num_targets = 0
    
    # Setup graphics
    mywin = visual.Window([1600, 900], color=[1,1,1], monitor="testMonitor", units="deg", fullscr=True)
    mywin.flip()
    mywin.flip()
    
    # setup instructions list
    def show_instructions(duration):

        instruction_text = """
        Welcome to the color experiment! 

        Stay still, focus on the centre of the screen, and try not to blink.

        This block will run for %s seconds.

        Press spacebar to continue. 

        """
        
        instruction_text = instruction_text % duration

        # graphics
        mywin.mouseVisible = False
        mywin.flip()
        mywin.flip()

        # Instructions
        text = visual.TextStim(win=mywin, text=instruction_text, color=[-1, -1, -1])
        text.draw()
        mywin.flip()
        event.waitKeys(keyList="space")
    
    # Setup trial list
    image_type = np.random.binomial(1, 0.15, n_trials)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # Setup stimuli
    nontargets = list(glob(os.path.join(COLORS_OBJECTS, "color", "*.png")))
    targets = list(glob(os.path.join(COLORS_OBJECTS, "odd", "*.png")))
    stim = [nontargets, targets]
    stimlist = []
    
    # Show instructions
    show_instructions(duration=duration)

    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            save_fn = generate_save_fn(eeg.device_name, "color_oddball2", "unnamed")
            print(
                f"No path for a save file was passed to the experiment. Saving data to {save_fn}"
            )
        eeg.start(save_fn, duration=record_duration)

    # Iterate through the events
    start = time()
    for ii, trial in trials.iterrows():
        # Inter trial interval
        core.wait(iti + np.random.rand() * jitter)
        is_target = "Non-target"
        
        # Select and display image
        label = trials["image_type"].iloc[ii]
        image_stim = choice(targets if label == 1 else nontargets)
        if label == 1:
            num_targets += 1
            is_target = "Target"
        image = load_image(image_stim)
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
        tempArray = [ii, image_stim, is_target]
        stimlist.append(tempArray)
        
        # offset
        core.wait(soa)
        mywin.flip()
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break

        event.clearEvents()
    
    # save list of stimuli
    directory = os.path.join(
        os.path.expanduser("~"),
        ".eegnb",
        "data",
        "color_oddball2",
        "behaviour",
        "subject" + str(subject),
        "session" + str(session)
    )
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    columns_head = ["trial", "stimuli", "target",]
    output = DataFrame(stimlist)
    outname = os.path.join(
        directory,
        "subject"
        + str(subject)
        + "_session"
        + str(session)
        + "stimlist.csv")
    output.to_csv(path_or_buf = outname, header = columns_head)
    
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

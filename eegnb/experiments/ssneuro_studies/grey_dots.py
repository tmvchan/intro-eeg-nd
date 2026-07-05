import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event, logging
from time import time, strftime, gmtime
from optparse import OptionParser
from pylsl import StreamInfo, StreamOutlet
from glob import glob
from random import choice
import random
import math
import os
import scipy.io

from eegnb import generate_save_fn
from eegnb.stimuli import CAT_DOG, LETTER_SYMBOL, RED_BLUE

__title__ = "Visual P300"


def present(subject, session, duration=120, eeg=None, save_fn=None):
    n_trials = int(
        (duration - 3 - 2)
        / (0.5 + 0.5)
    )
    iti = 0.5
    soa = 0.5
    jitter = 0
    record_duration = np.float32(duration)
    markernames = [1, 2]
    num_targets = 0
    
    # Setup trial list
    image_type = np.random.binomial(1, 0.2, n_trials)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))
    
    # Setup graphics
    mywin = visual.Window([1600, 900], color=[1,1,1], monitor="testMonitor", units="deg", fullscr=True)
    mywin.flip()
    mywin.flip()
    
    def show_instructions(duration):

        instruction_text = """
            Welcome to the P300 experiment! 

            Stay still, focus on the centre of the screen, and try not to blink.

            This block will run for %s seconds.

            Press spacebar to continue. 

            """
        instruction_text = instruction_text % duration

        # Instructions
        text = visual.TextStim(win=mywin, text=instruction_text, color=[-1, -1, -1])
        text.draw()
        mywin.flip()
        event.waitKeys(keyList="space")

        mywin.mouseVisible = False
    
    image = visual.Circle(
        mywin, 
        lineColor="#000000", 
        lineWidth=3.0, 
        radius= 60 / 2, 
        edges=32, 
        units="pix",
        name = "circle"
    )
    
    grey_list = ['#696969', '#484848', '#808080', '#BEBEBE', '#A0A0A0']
    color_list = ['blue', 'orange', 'yellow', 'red', 'pink']
    responses = []

    # Show instructions
    show_instructions(duration=duration)

    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            save_fn = generate_save_fn(eeg.device_name, "grey_dots", "unnamed")
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
        if label == 1: # target
            num_targets += 1
            image.fillColor = choice(color_list)
            target_text = "target"
        elif label == 0: # non-target
            image.fillColor = choice(grey_list)
            target_text = "non-target"
        image_color = image.fillColor
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
        
        tempArray = [ii + 1, target_text, image_color]
        responses.append(tempArray)
        
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
    
    # write behavioural output file
    directory = os.path.join(
        os.path.expanduser("~"),
        ".eegnb",
        "data",
        "grey_dots",
        "behaviour",
        "subject" + str(subject),
        "session" + str(session)
    )
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    # make output
    column_labels = [
            "trial",
            "is target",
            "stimulus color",
        ]
    output = DataFrame(responses)
    outname = os.path.join(
        directory,
        "subject"
        + str(subject)
        + "_session"
        + str(session)
        + ("_behOutput_%s.csv" % strftime("%Y-%m-%d-%H.%M.%S", gmtime())),
    )
    output.to_csv(path_or_buf = outname, header = column_labels)




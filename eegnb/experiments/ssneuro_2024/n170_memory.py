from psychopy import prefs
#change the pref libraty to PTB and set the latency mode to high precision
prefs.hardware['audioLib'] = 'PTB'
prefs.hardware['audioLatencyMode'] = 3

import os
from time import time, strftime, gmtime
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

__title__ = "N170 Memory Faces"

# current problems
    # we need to input the behavioral task aspect of our experiment
        # how would you rate the coloring of the object? 
            # need to figure out timing aspects for this as well
    # we need to smooth out all of the image conditions due to our different sets of stimuli

def present(duration=60, eeg: EEG=None, save_fn=None,
            n_trials = 40, iti = 3, soa = 1, jitter = 0.2, subject=0, session=0):
    
    record_duration = np.float32(duration)
    markernames = [1, 2]

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # start the EEG stream, will delay 5 seconds to let signal settle

    # Setup graphics
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)
    
    # save file names
    men_fns = glob(os.path.join(MEN_WOMEN, "Men", "Study Men", "*.jpg"))
    women_fns = glob(os.path.join(MEN_WOMEN, "Women", "Study Women", "*.jpg"))
    
    shuffle(men_fns)
    shuffle(women_fns)
    
    men = list(map(load_image, men_fns))
    women = list(map(load_image, women_fns))
    stim = [men, women]
    
    # Setup trial list
    # image_type = np.random.binomial(1, 0.5, n_trials)
    image_type = np.zeros(len(men))
    image_type = np.append(image_type, np.full(len(women), 1))
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
    men_idx = 0
    women_idx = 0

    # Iterate through the events
    for ii, trial in trials.iterrows():
        # Inter trial interval
        core.wait(iti + np.random.rand() * jitter)

        label = trials["image_type"].iloc[ii]
        if label == 0:
            image = men[men_idx]
            men_idx += 1
        elif label == 1:
            image = women[women_idx]
            women_idx += 1
        image.draw()

         # trial begins here: intertrial interval
        core.wait(iti + np.random.rand() * jitter)

        # Push sample
        if eeg:
            timestamp = time()
            if eeg.backend == "muselsl":
                marker = [markernames[label]]
            else:
                marker = markernames[int(label)]
            eeg.push_sample(marker=marker, timestamp=timestamp)

        mywin.flip()
        
        # Stimulus offset / response begin
        core.wait(soa)
        
        # wait until response + resp offset
        mywin.flip()
        
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break

        event.clearEvents()
    
    # write out order that the faces were presented in
    directory = os.path.join(
        os.path.expanduser("~"),
        ".eegnb",
        "data",
        "men_women",
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
        + ("_behOutput_%s.csv" % strftime("%Y-%m-%d-%H.%M.%S", gmtime())),
    )
    output = DataFrame(men_fns, women_fns)
    output.to_csv(path_or_buf = outname)
    
    # Cleanup
    if eeg:
        eeg.stop()

    mywin.close()


def show_instructions():
  
    # change "side keyboard" portion and numbering depending on what we are able to figure out
    instruction_text = """
    Welcome to the face memory task!
    
    Please look at each face and carefully remember it, as you will be tested after.
 
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
    
    
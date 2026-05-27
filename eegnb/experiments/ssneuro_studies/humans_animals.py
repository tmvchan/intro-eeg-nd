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

__title__ = "Visual N170 comparing animals and humans"


def present(duration=120, subject = 0, session = 0, eeg: EEG=None, save_fn=None,
            n_trials = 2010, iti = 0.4, soa = 0.3, jitter = 0.2):
    
    n_trials = int(
        duration / (iti + soa)
    )
    
    record_duration = np.float32(duration)
    markernames = [1, 2, 3] # 1: human, 2: pets, 3: foreign animals

    # Setup trial list
    image_type = np.random.randint(low = 0, high = 3, size = n_trials)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # start the EEG stream, will delay 5 seconds to let signal settle

    # Setup graphics
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)

    human = list(glob(os.path.join(HUMAN_ANIMAL, "human", "*.jpg")))
    pets = list(glob(os.path.join(HUMAN_ANIMAL, "pets_2", "*.jpg")))
    foreign = list(glob(os.path.join(HUMAN_ANIMAL, "foreign_2", "*.jpg")))
    stim = [human, pets, foreign]
    stimlist = []
    
    def show_instructions(duration):

        instruction_text = """
        Welcome to the N170 experiment! 

        Stay still, focus on the centre of the screen, and try not to blink. 

        This block will run for %s seconds.

        Press spacebar to continue. 

        """
        instruction_text = instruction_text % duration
        
        # Instructions
        text = visual.TextStim(win=mywin, text=instruction_text, color=[-1, -1, -1])
        text.draw()
        mywin.mouseVisible = False
        mywin.flip()
        event.waitKeys(keyList="space")
    
    # Show the instructions screen
    show_instructions(duration)
    
    mywin.flip()
    core.wait(3)
    
    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            random_id = random.randint(1000,10000)
            save_fn = generate_save_fn(eeg.device_name, "humans_animals", random_id, random_id, "unnamed")
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
        
        if label == 0:
            image = choice(human)
        elif label == 1:
            image = choice(pets)
        elif label == 2:
            image = choice(foreign)
        image_stim = load_image(image)
        image_stim.draw()

        # Push sample
        if eeg:
            timestamp = time()
            if eeg.backend == "muselsl":
                marker = [markernames[label]]
            else:
                marker = markernames[label]
            eeg.push_sample(marker=marker, timestamp=timestamp)
        
        tempArray = [ii, image]
        stimlist.append(tempArray)
        
        mywin.flip()

        # offset
        core.wait(soa)
        mywin.flip()
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break

        event.clearEvents()

    # print stimulus list for future ref.
    subject_str = f"subject{subject:04}"
    session_str = f"session{session:03}"
    
    directory = os.path.join(
        os.path.expanduser("~"),
        ".eegnb",
        "data",
        "humans_animals",
        subject_str,
        session_str
    )
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    columns_head = ["trial", "stimuli", ]
    output = DataFrame(stimlist)
    outname = os.path.join(
        directory,
        "subject"
        + str(subject)
        + "_session"
        + str(session)
        + "stimlist.csv")
    output.to_csv(path_or_buf = outname, header = columns_head)    
    
    # Cleanup
    if eeg:
        eeg.stop()

    mywin.close()




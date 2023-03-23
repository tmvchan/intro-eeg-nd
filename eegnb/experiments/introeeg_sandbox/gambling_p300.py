# An attempt to ensure that I can code a gambling task into the PsychoPy environment.
# T. M. Vanessa Chan
# March 2023

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

__title__ = "Gambling Task"


def present(duration=150, eeg: EEG=None, save_fn=None, subject=0, session=0,
            n_trials = 30, iti = random.choice([1.4, 2, 2.75]), soa = 0.3, jitter = 0.4):
    
    record_duration = np.float32(duration)
    markernames = [1, 2]

    # Setup trial list
    trial_type = np.random.randint(0, 2, n_trials)
    trials = DataFrame(dict(trial_type=trial_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # start the EEG stream, will delay 5 seconds to let signal settle

    # Setup graphics
    mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True)

    #RedCirc = list(map(load_image, glob(os.path.join(RED_CIRCLE, "*.png"))))
    #stim = RedCirc
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
    
    core.wait(iti + np.random.rand() * jitter)
    
    # Iterate through the events
    for ii, trial in trials.iterrows():
        
        # Inter trial interval
        # core.wait(iti + np.random.rand() * jitter)
        
        # Select condition
        label = trials["trial_type"].iloc[ii]
        
        # Based on condition, draw the appropriate stimulus
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

        # while loop: continue to loop until a key response is recorded
        # we want this to loop until the end of SOA + ITI period
        # RTs will be taken until the end of the SOA + ITI period (approx. 1.4-3 seconds).

        stimtime = soa + iti + np.random.rand() * jitter
        # now_time = clock.getTime()
        # timediff = now_time - respstart
        rt = 0
        win_flipped = 0
        keyrec = 0

        while clock.getTime() - respstart < stimtime: 
            # get response
            keys = event.getKeys(keyList="space", timeStamped = clock)

            if keys and keyrec == 0:
                # reaction time calculation
                rt = keys[0][1] - respstart
                keyrec = 1 # only keep the first keypress
            
            if clock.getTime() - respstart > soa and win_flipped == 0:
                mywin.flip()
                win_flipped = 1 # flip the window only once 
        else:
            timediff = stimtime
          
        # save RT
        tempArray = [int(ii + 1), rt * 1000]
        responses.append(tempArray)
        
        mywin.flip()
        core.wait(stimtime - timediff)

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

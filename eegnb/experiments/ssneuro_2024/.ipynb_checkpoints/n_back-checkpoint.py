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
from pandas import DataFrame, read_csv, Series
from psychopy import visual, core, event

from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG
from eegnb import stimuli, experiments

exp_dir = os.path.split(experiments.__file__)[0]

# fixed stim order list file
word_list_file = os.path.join(exp_dir, "ssneuro_2024", "nback_music.csv")

__title__ = "Verbal N-Back"


def present(duration=120, eeg: EEG=None, save_fn=None,
            n_trials = 2010, iti = 1, soa = 3, jitter = 0.2, subject=0, session=0, ver=1):
    
    record_duration = np.float32(duration)
    markernames = [1, 2] # non-repeat, repeat

    # Setup trial list
    trial_type = np.random.binomial(1, 0.3, n_trials) # number of 2-back repeats
    # because we can't have the earliest 1 be any earlier than position 3, insert 2 zeros in front of every list
    trial_type = np.insert(trial_type, 0, 0)
    trial_type = np.insert(trial_type, 0, 0)
    trials = DataFrame(dict(trial_type=trial_type, timestamp=np.zeros(len(trial_type))))

    word_lists = read_csv(word_list_file)
    
    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    def load_text(stim_text):
        return visual.TextStim(win=mywin, text=stim_text, color=[-1,-1,-1])
    
    # start the EEG stream, will delay 5 seconds to let signal settle

    # Setup graphics
    mywin = visual.Window([1600, 900], color=[1,1,1], monitor="testMonitor", units="deg", fullscr=True)
    mywin.flip() # makes background white
    mywin.flip()
    
    words = word_lists.iloc[:,ver-1]

    # Set up response array: saving trial information for output
    responses = []

    # Show the instructions screen
    show_instructions(duration)

    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            random_id = random.randint(1000,10000)
            save_fn = generate_save_fn(eeg.device_name, "verbal_nback", random_id, random_id, "unnamed")
            print(
                f"No path for a save file was passed to the experiment. Saving data to {save_fn}"
            )
        eeg.start(save_fn, duration=record_duration + 5)

    # create a clock for rt's
    clock = core.Clock()
        
    # Start EEG Stream, wait for signal to settle, and then pull timestamp for start point
    start = time()

    one_back = 'oneback'
    two_back = 'twoback'
    
    # Iterate through the events
    for ii, trial in trials.iterrows():
        # Inter trial interval
        core.wait(iti + np.random.rand() * jitter)

        # Select and display image
        label = trials["trial_type"].iloc[ii]
        #image = choice(faces if label == 1 else houses)
        
        word = two_back if label == 1 else choice([ele for ele in words if ele != two_back])
        text = load_text(word)
        text.draw()

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
        rt = None
        win_flipped = 0
        keyrec = 0

        while clock.getTime() - respstart < stimtime:
            # get response
            keys = event.getKeys(keyList="space", timeStamped=clock)

            if keys and keyrec == 0:
                # reaction time calculation
                rt = keys[0][1] - respstart
                keyrec = 1  # only keep the first keypress

            if clock.getTime() - respstart > soa and win_flipped == 0:
                mywin.flip()
                win_flipped = 1  # flip the window only once
        else:
            timediff = stimtime

        # save trial info into array
        if rt is None:
            reactiontime = 'No Response'
        else:
            reactiontime = rt * 1000
        
        tempArray = [ii + 1, label + 1, word, reactiontime]
        responses.append(tempArray)
        column_labels = [
            "trial",
            "target type",
            "target",
            "reaction time"
        ]
        
        mywin.flip()
        core.wait(stimtime - timediff)

        # offset
        # core.wait(soa)
        
        # modify one/twoback
        two_back = one_back
        one_back = word
        
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break

        event.clearEvents()

    # write behavioural output file
    directory = os.path.join(
        os.path.expanduser("~"),
        ".eegnb",
        "data",
        "n_back",
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
    output = DataFrame(responses)
    output.to_csv(path_or_buf = outname, header = column_labels)

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
    mywin = visual.Window([1600, 900], color=[1,1,1], monitor="testMonitor", units="deg", fullscr=True)

    mywin.mouseVisible = False

    # Instructions
    text = visual.TextStim(win=mywin, text=instruction_text, color=[-1, -1, -1])
    text.draw()
    mywin.flip()
    event.waitKeys(keyList="space")

    mywin.mouseVisible = True
    mywin.close()

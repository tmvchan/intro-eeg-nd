import os
from time import time
from glob import glob
from random import choice

import numpy as np
from pandas import DataFrame, read_csv, Series
from psychopy import visual, core, event

from eegnb import generate_save_fn
#from eegnb.stimuli import CAT_DOG, LETTER_SYMBOL, RED_BLUE

from eegnb import stimuli, experiments

stim_dir = os.path.split(stimuli.__file__)[0]
exp_dir = os.path.split(experiments.__file__)[0]

# fixed stim order list file
word_list_file = os.path.join(exp_dir, "introeeg_sandbox", "words_list.csv")

__title__ = "Words and Memory"

def present(duration=120, eeg=None, save_fn=None, subject=0, session=0, ver=1):
    iti = 0.4
    soa = 0.3
    jitter = 0.2
    record_duration = np.float32(duration)
    markernames = [1]
    
    # Setup trial list
    #image_type = np.random.binomial(1, 0.15, n_trials)
    word_lists = read_csv(word_list_file)
    n_trials = word_lists.shape[0]
    #trials = DataFrame(dict(word_, timestamp=np.zeros(n_trials)))
    
    def load_text(stim_text):
        return visual.TextStim(win=mywin, text=stim_text, color=[-1,-1,-1])

    # Setup graphics
    mywin = visual.Window([1600, 900], color=[1,1,1], monitor="testMonitor", units="deg", fullscr=True)
    mywin.flip()
    mywin.flip()
    words = word_lists.iloc[:,ver-1]
    # shuffle word list
    stim = words.sample(frac=1).reset_index(drop=True)

    # Show instructions
    show_instructions(duration=duration, ver=ver)

    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            save_fn = generate_save_fn(eeg.device_name, "words_memory", "unnamed")
            print(
                f"No path for a save file was passed to the experiment. Saving data to {save_fn}"
            )
        eeg.start(save_fn, duration=record_duration)
    
    # Iterate through the events
    start = time()
    
    for ii, trial in stim.items():
        # Inter trial interval
        core.wait(iti + np.random.rand() * jitter)

        # Select and display text
        #label = trials["image_type"].iloc[ii]
        word = trial
        text = load_text(word)
        text.draw()

        # Push sample
        if eeg:
            timestamp = time()
            if eeg.backend == "muselsl":
                marker = [markernames[label]]
            else:
                marker = markernames[0]
            eeg.push_sample(marker=marker, timestamp=timestamp)

        mywin.flip()

        # offset
        core.wait(soa)
        mywin.flip()
        
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break

        event.clearEvents()
    
    directory = os.path.join(
        os.path.expanduser("~"),
        ".eegnb",
        "data",
        "words_memory",
        "subject" + str(subject),
        "session" + str(session)
    )

    if not os.path.exists(directory):
        os.makedirs(directory)

    outname = os.path.join(
        directory,
        "subject" + str(subject) + "_session" + str(session) + "_words.csv"
    )
    
    stim.to_csv(path_or_buf=outname)
    
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


def show_instructions(duration, ver):

    if ver is 1: 
        instruction_text = """
        Welcome to the P300 experiment! 

        Stay still, focus on the centre of the screen, and try not to blink. Try to count the number of times a cat appears.

        This block will run for %s seconds.

        Press spacebar to continue. 

        """
    elif ver is 2:
        instruction_text = """
        Welcome to the P300 experiment! 

        Stay still, focus on the centre of the screen, and try not to blink. Try to count the number of times a question mark (?) appears.

        This block will run for %s seconds.

        Press spacebar to continue. 

        """
    elif ver is 3:
        instruction_text = """
        Welcome to the P300 experiment! 

        Stay still, focus on the centre of the screen, and try not to blink. Try to count the number of times a red circle appears.

        This block will run for %s seconds.

        Press spacebar to continue. 

        """
    instruction_text = instruction_text % duration

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

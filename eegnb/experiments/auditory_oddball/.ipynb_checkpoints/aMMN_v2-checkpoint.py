import os
from time import time, sleep
from glob import glob
from random import choice
from optparse import OptionParser

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event, sound

from eegnb import generate_save_fn

from psychopy import prefs
#change the pref libraty to PTB and set the latency mode to high precision
prefs.hardware['audioLib'] = 'PTB'
prefs.hardware['audioLatencyMode'] = 3


def present(
    save_fn: str = None,
    duration=120,
    iti=0.3,
    soa=0.2,
    jitter=0.2,
    secs=0.07,
    volume=0.8,
    eeg=None,
):
    
    markernames = [1, 2]
    record_duration = np.float32(duration)
    n_trials = int(duration/(secs+iti))

    ## Initialize stimuli
    # aud1 = sound.Sound('C', octave=5, sampleRate=44100, secs=secs)
    aud1 = sound.Sound(440, secs=secs)  # , octave=5, sampleRate=44100, secs=secs)
    aud1.setVolume(volume)

    # aud2 = sound.Sound('D', octave=6, sampleRate=44100, secs=secs)
    aud2 = sound.Sound(528, secs=secs)
    aud2.setVolume(volume)
    auds = [aud1, aud2]

    # Setup trial list
    stim_types = np.random.binomial(1, 0.15, n_trials)
    itis = np.ones(n_trials) * 0.5
    trials = DataFrame(dict(sound_ind=stim_types, iti=itis))

    # for col_name, col_vec in additional_labels.items():
    #    trials[col_name] = col_vec

    # Setup graphics
    mywin = visual.Window(
        [1920, 1080], monitor="testMonitor", units="deg", fullscr=True
    )
    fixation = visual.GratingStim(win=mywin, size=0.2, pos=[0, 0], sf=0, rgb=[1, 0, 0])
    fixation.setAutoDraw(True)
    mywin.flip()
    
    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        eeg.start(save_fn, duration=record_duration)

    show_instructions(duration)

    # Start EEG Stream, wait for signal to settle, and then pull timestamp for start point
    start = time()

    # Iterate through the events
    for ii, trial in trials.iterrows():

        # Inter trial interval
        core.wait(trial["iti"])

        # Select and display image
        ind = int(trial["sound_ind"])
        auds[ind].stop()
        auds[ind].play()

        # Push sample
        if eeg:
            timestamp = time()
            if eeg.backend == "muselsl":
                marker = [markernames[ind]]
                marker = list(map(int, marker))
            else:
                marker = [markernames[ind]]
            eeg.push_sample(marker=marker, timestamp=timestamp)

        mywin.flip()
        if len(event.getKeys()) > 0:
            break
        if (time() - start) > record_duration:
            break

        event.clearEvents()

    # Cleanup
    if eeg:
        eeg.stop()

    mywin.close()


def show_instructions(duration):

    instruction_text = """
    Welcome to the aMMN experiment! 
 
    Stay still, focus on the centre of the screen, and try not to blink. 

    This block will run for %s seconds.

    Press spacebar to continue. 
    
    """
    instruction_text = instruction_text % duration

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

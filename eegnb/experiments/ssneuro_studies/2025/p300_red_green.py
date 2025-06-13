import os
from time import time, strftime, gmtime
from glob import glob
from random import choice

import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event

from eegnb import generate_save_fn
from eegnb.stimuli import RED_GREEN

__title__ = "Visual P300 with response button"


def present(duration=120, eeg=None, save_fn=None, subject=0, session=0):
    n_trials = 2010
    iti = 0.4
    soa = 0.4
    jitter = 0.2
    record_duration = np.float32(duration)
    markernames = [1, 2]

    # Setup trial list
    image_type = np.random.binomial(1, 0.3, n_trials)
    trials = DataFrame(dict(image_type=image_type, timestamp=np.zeros(n_trials)))

    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)

    # Setup graphics
    mywin = visual.Window([1600, 900], color=[1,1,1], monitor="testMonitor", units="deg", fullscr=True)
    clock = core.Clock()
    responses = []
    target_type = []
    mywin.flip()
    mywin.flip()
    
    targets = list(map(load_image, glob(os.path.join(RED_GREEN, "green_circle.png"))))
    nontargets = list(map(load_image, glob(os.path.join(RED_GREEN, "red_circle.png"))))
    stim = [nontargets, targets]

    # Show instructions
    show_instructions(duration=duration)

    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            save_fn = generate_save_fn(eeg.device_name, "P300_red_green", "unnamed")
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
        image = choice(targets if label == 1 else nontargets)
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
        rt = None
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
        if rt is None:
            tempArray = [int(ii + 1), 'No Response']
        else:
            tempArray = [int(ii + 1), rt * 1000]
        responses.append(tempArray)
        target_type.append(markernames[label])

        # offset
        core.wait(soa)
        mywin.flip()
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break

        event.clearEvents()

    # write behavioural output file
    directory = os.path.join(
        os.path.expanduser("~"),
        ".eegnb",
        "data",
        "P300_red_green",
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
    output = DataFrame(target_type, responses)
    output.to_csv(path_or_buf = outname)

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
 
    Stay still, focus on the centre of the screen, and try not to blink. 
    
    Push the spacebar when you see the green circle.

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

    #mywin.mouseVisible = True
    mywin.close()

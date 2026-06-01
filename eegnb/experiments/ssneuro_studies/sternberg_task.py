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
from eegnb.stimuli import LETTER_SYMBOL

########################### Sternberg Item Recognition Test ###########################

# Test involves presenting a set of items and then a probe item that may or may not be in the original list
# Participants must answer either yes 'f' or no 'j' to the probe item
# Record accuracy and RT to each trial, go through at least 30 trials.
# Manipulate item list length (list_len) and symbol type (ver). 
# Typically, participants' RT increases with length of list. Perhaps also will be harder with more difficult / less verbalizable symbols?

def present(subject, session, eeg=None, save_fn=None, yesProb = 0.5, isi = 0.5, jitter = 0, list_len = 4, ver = 1, trial_count = 30):

    # write behavioural output file
    directory = os.path.join(
        os.path.expanduser("~"),
        ".eegnb",
        "data",
        "sternberg",
        "behaviour",
        "subject" + str(subject),
        "session" + str(session)
    )
    if not os.path.exists(directory):
        os.makedirs(directory)

    markernames = [1, 2, 3] # 1: stim list, 2: probe yes, 3: probe no
    #record_duration = np.float32(duration)

    # code modified from https://github.com/djangraw/PsychoPyParadigms/blob/master/BasicExperiments/GoNoGoTask_d1.py

    # declare primary task params
    params = {
        # Declare stimulus and response parameters
        # time when stimulus is presented (in seconds)
        "stimDur": 0.8,
        # time between when one stimulus disappears and the next appears (in seconds)
        "ISI": 0.5,
        "tStartup": 3,  # pause time before starting first stimulus
        "tCoolDown": 2,  # pause time after end of last stimulus before "the end" text
        "triggerKey": "t",  # key from scanner that says scan is starting
        # keys to be used for responses (mapped to 1,2,3,4)
        "respKeys": ["f", "j"],
        "goStim": "square",  # shape signaling respond
        "noGoStim": "diamond",  # shape signaling don't respond
        "goStimProb": 0.75,  # probability of a given trial being a 'go' trial
        # declare prompt and question files
        "skipPrompts": False,  # go right to the scanner-wait page
        "promptDir": "Prompts/",  # directory containing prompts and questions files
        "promptFile": "GoNoGoPrompts.txt",  # Name of text file containing prompts
        # declare display parameters
        "fullScreen": True,  # run in full screen mode?
        # display on primary screen (0) or secondary (1)?
        "screenToShow": 0,
        "fixCrossSize": 60,  # size of cross, in pixels
        # (x,y) pos of fixation cross displayed before each stimulus (for gaze drift correction)
        "fixCrossPos": [0, 0],
        # in rgb255 space: (r,g,b) all between 0 and 255
        "screenColor": (255, 255, 255),
    }

    #n_trials = int(
    #    (duration - params["tStartup"] - params["tCoolDown"])
    #    / (params["ISI"] + params["stimDur"])
    #)
    
    n_trials = trial_count
    screenRes = [800, 600]

    # create clocks and window
    globalClock = core.Clock()  # to keep track of time
    trialClock = core.Clock()  # to keep track of time
    win = visual.Window(
        screenRes,
        fullscr=params["fullScreen"],
        allowGUI=False,
        monitor="testMonitor",
        screen=params["screenToShow"],
        units="deg",
        name="win",
        color=params["screenColor"],
        colorSpace="rgb255",
    )
    win.mouseVisible = False
    # create fixation cross
    fCS = params["fixCrossSize"]  # size (for brevity)
    fCP = params["fixCrossPos"]  # position (for brevity)
    fixation = visual.ShapeStim(
        win,
        lineColor="#000000",
        lineWidth=3.0,
        vertices=(
            (fCP[0] - fCS / 2, fCP[1]),
            (fCP[0] + fCS / 2, fCP[1]),
            (fCP[0], fCP[1]),
            (fCP[0], fCP[1] + fCS / 2),
            (fCP[0], fCP[1] - fCS / 2),
        ),
        units="pix",
        closeShape=False,
        name="fixCross",
    )
    # create text stimuli
    message1 = visual.TextStim(
        win,
        pos=[0, +0.5],
        wrapWidth=1.5,
        color="#000000",
        alignHoriz="center",
        name="topMsg",
        text="aaa",
        units="norm",
    )
    message2 = visual.TextStim(
        win,
        pos=[0, 0],
        wrapWidth=1.5,
        color="#000000",
        alignHoriz="center",
        name="middleMsg",
        text="bbb",
        units="norm",
    )
    message3 = visual.TextStim(
        win,
        pos=[0, -0.5],
        wrapWidth=1.5,
        color="#000000",
        alignHoriz="center",
        name="bottomMsg",
        text="bbb",
        units="norm",
    )
    
    # graphics

    def load_image(filename):
        return visual.ImageStim(win=win, image=filename)

    #mywin = visual.Window([900, 500], monitor="testMonitor", units="deg", fullscr=False)
    if ver is 1: # letters
        targets_paths = list(glob(os.path.join(LETTER_SYMBOL, "letter-*.png")))
    elif ver is 2: # digits
        targets_paths = list(glob(os.path.join(LETTER_SYMBOL, "D*.png")))
    elif ver is 3: # weird symbols
        targets_paths = list(glob(os.path.join(LETTER_SYMBOL, "P*.png")))
    
    # Pre-load PsychoPy Image Objects so there is 0 disk latency during the trials
    targets = [visual.ImageStim(win=win, image=p) for p in targets_paths]

    
    # draw stimuli
    fCS_rt2 = fCS / math.sqrt(2)
    tNextFlip = [0.0]

    def AddToFlipTime(tIncrement=1.0):
        tNextFlip[0] += tIncrement

    # define start function
    def show_instructions():
        message1.setText("Welcome to the experiment! On each trial, you will be shown a short list of symbols and then a probe. The probe will be preceded by a red cross.")
        message2.setText("Press 'f' if the probe was part of the previous list of symbols, and 'j' if the probe was not part of the previous list of symbols.")
        message3.setText("Respond as quickly and accurately as possible. Press 'd' to begin.")
        win.logOnFlip(level=logging.EXP, msg="Display TheStart")
        message1.draw()
        message2.draw()
        message3.draw()
        win.flip()
        thisKey = event.waitKeys(keyList=["d"])
        event.clearEvents()
        fixation.draw()
        win.flip()
    
    # define end function
    def CoolDown():
        message2.setText("Press 'q' or 'escape' to end the session.")
        win.logOnFlip(level=logging.EXP, msg="Display TheEnd")
        message2.draw()
        win.flip()
        thisKey = event.waitKeys(keyList=["q", "escape"])

        # Cleanup
        if eeg:
            eeg.stop()
        
        # exit
        win.close()
        core.quit()
    
    # record responses, accuracy, etc. (added by AE)
    responses = []
    stimlist = []
    hits_yes = 0
    hits_no = 0
    fa_yes = 0
    fa_no = 0
    count_yes = 0
    count_no = 0
    correct = 0
    rt = np.zeros((n_trials, 1))
    
    show_instructions()
    
    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            save_fn = generate_save_fn(eeg.device_name, "sternberg", "unnamed")
            print(
                f"No path for a save file was passed to the experiment. Saving data to {save_fn}"
            )
        eeg.start(save_fn)

    for iTrial in range(0, n_trials):

        # Decide Trial Params
        isYesTrial = random.random() < yesProb

        # display info to experimenter
        print(
            (
                "Running Trial %d: isGo = %d, ISI = %.1f"
                % (iTrial, isYesTrial, params["ISI"])
            )
        )

        if iTrial == 0:
            tNextFlip[0] = globalClock.getTime() + 5.0
        fixation.draw()
        while globalClock.getTime() < tNextFlip[0]:
            pass
        win.flip()
        tStimStart = globalClock.getTime()  # record time when window flipped
        # set up next win flip time after this one
        AddToFlipTime(isi + np.random.rand() * jitter)  # add to tNextFlip[0]
        
        # If a late response pushed actual time past the next scheduled flip, 
        # reset tNextFlip to the current time so it doesn't skip the first stimulus.
        if globalClock.getTime() > tNextFlip[0]:
            tNextFlip[0] = globalClock.getTime()
        
        # Set up stimuli in list
        image_list = np.random.choice(targets, list_len, replace = False)
        image_other = [item for item in targets if item not in image_list] # for if the probe is not in list
        
        # Loop through image_list to show all stimuli
        for ii, stim in enumerate(image_list):
            label = 0
            stim_name = stim.image
            stim.draw()
            win.logOnFlip(
                level=logging.EXP, msg="Display list stim" #(%s)" % params["goStim"]
            )
            timestamp = time()
            #outlet.push_sample([markernames[0]], timestamp)
            if eeg:
                if eeg.backend == "muselsl":
                    marker = [markernames[label]]
                else:
                    marker = markernames[label]
                eeg.push_sample(marker=marker, timestamp=timestamp)
            
            # Wait until it's time to display
            while globalClock.getTime() < tNextFlip[0]:
                pass
            # log & flip window to display image
            win.flip()
            tStimStart = globalClock.getTime()  # record time when window flipped
            # set up next win flip time after this one
            AddToFlipTime(params["stimDur"])  # add to tNextFlip[0]
            
            # prep for fixation
            while globalClock.getTime() < tNextFlip[0]:
                pass
            
            tempArray1 = [iTrial, stim_name]
            stimlist.append(tempArray1)
            
            # Display the fixation cross
            if isi > 0:  # if there should be a fixation cross
                if ii is 3:
                    fixation.color = 'red'
                fixation.draw()  # draw it
                win.logOnFlip(level=logging.EXP, msg="Display Fixation")
                win.flip()
                AddToFlipTime(isi + np.random.rand() * jitter)  # add to tNextFlip[0]
            
        # Draw probe stim
        if isYesTrial:
            label = 1
            image = choice(image_list)
            probe_name = image.image
            image.draw()
            win.logOnFlip(
                level=logging.EXP, msg="Display yes stim" #(%s)" % params["goStim"]
            )
            timestamp = time()
            #outlet.push_sample([markernames[0]], timestamp)
            if eeg:
                if eeg.backend == "muselsl":
                    marker = [markernames[label]]
                else:
                    marker = markernames[label]
                eeg.push_sample(marker=marker, timestamp=timestamp)
        else:
            label = 2
            image = choice(image_other)
            probe_name = image.image
            image.draw()
            win.logOnFlip(
                level=logging.EXP, msg="Display no stim" #(%s)" % params["noGoStim"]
            )
            timestamp = time()
            #outlet.push_sample([markernames[1]], timestamp)
            if eeg:
                if eeg.backend == "muselsl":
                    marker = [markernames[label]]
                else:
                    marker = markernames[label]
                eeg.push_sample(marker=marker, timestamp=timestamp)
                
        # Wait until it's time to display
        while globalClock.getTime() < tNextFlip[0]:
            pass
        # log & flip window to display image
        win.flip()
        tStimStart = globalClock.getTime()  # record time when window flipped
        # set up next win flip time after this one
        AddToFlipTime(params["stimDur"])  # add to tNextFlip[0]

        # Flush the key buffer and mouse movements
        event.clearEvents()
        # Wait for relevant key press or 'stimDur' seconds
        respKey = None
        thisKey = None
        t = None
        # until it's time for the next frame
        while globalClock.getTime() < tNextFlip[0]:
            # get new keys
            newKeys = event.waitKeys(keyList=params['respKeys']+['q','escape'],timeStamped=globalClock)
            #newKeys = event.getKeys(timeStamped=globalClock)
            # check each keypress for escape or response keys
            if len(newKeys) > 0:
                for thisKey in newKeys:
                    respKey = thisKey[0]
                    t = globalClock.getTime() - tStimStart
                    # tempArray = [iTrial, isGoTrial, respKey[0]]
                    # responses.append(tempArray)
                    if thisKey[0] in ["q", "escape"]:  # escape keys
                        CoolDown()  # exit gracefully
                    # only take first keypress
                    elif thisKey[0] in params["respKeys"] and respKey == None:
                        respKey = thisKey  # record keypress

        if isYesTrial:
            count_yes += 1
        else:
            count_no += 1

        if isYesTrial:
            if respKey == "f":
                hits_yes += 1
                resp_text = "Yes"
                correct = 1
            else:
                fa_yes += 1
                resp_text = "No"
        elif ~isYesTrial:
            if respKey == "j":
                hits_no += 1
                resp_text = "Yes"
                correct = 1
            else:
                fa_no += 1
                resp_text = "No"

        # get RT for correct trials only
        if correct is 1:
            rt[iTrial] = t
        else:
            rt[iTrial] = np.nan
        
        tempArray = [iTrial, isYesTrial, resp_text, t, probe_name]
        responses.append(tempArray)
        
        # Display the fixation cross
        if isi > 0:  # if there should be a fixation cross
            fixation.color = 'black'
            fixation.draw()  # draw it
            win.logOnFlip(level=logging.EXP, msg="Display Fixation")
            win.flip()
            AddToFlipTime(isi + np.random.rand() * jitter)  # add to tNextFlip[0]

        # return
        if iTrial == n_trials:
            AddToFlipTime(params["tCoolDown"])

    fixation.draw()
    win.flip()
    while globalClock.getTime() < tNextFlip[0]:
        pass

    acc_yes = np.round(float(hits_yes) / float(count_yes) * float(100), 2)
    acc_no = np.round(float(hits_no) / float(count_no) * float(100), 2)
    mean_rt = np.round(float(np.nanmean(rt)), 2)
    
    # make output
    column_labels = [
            "trial",
            "target type",
            "response",
            "rt",
            "probe stimulus",
        ]
    columns_2 = ["trial", "stimuli",]
    output = DataFrame(responses)
    output2 = DataFrame(stimlist)
    outname = os.path.join(
        directory,
        "subject"
        + str(subject)
        + "_session"
        + str(session)
        + ("_behOutput_%s.csv" % strftime("%Y-%m-%d-%H.%M.%S", gmtime())),
    )
    outname2 = os.path.join(
        directory,
        "subject"
        + str(subject)
        + "_session"
        + str(session)
        + "stimlist.csv")
    output.to_csv(path_or_buf = outname, header = column_labels)
    output2.to_csv(path_or_buf = outname2, header = columns_2)

    # display results
    message1.setText("That's the end! Press space to continue. Here are your results:")
    message2.setText(
        "N trials = %d \nYes accuracy = %d/%d (%0.2f) \nNo accuracy = %d/%d (%0.2f) \nMean Correct Trials RT = %0.2f"
        % (
            n_trials,
            hits_yes,
            count_yes,
            round(acc_yes, 2),
            hits_no,
            count_no,
            round(acc_no, 2),
            round(mean_rt, 2),
        )
    )
    message1.draw()
    message2.draw()
    win.flip()
    thisKey = event.waitKeys(keyList=["space"])
    CoolDown()

def main():
    parser = OptionParser()
    parser.add_option(
        "-s", "--subject", dest="subject", type="string", help="name of subject."
    )
    parser.add_option(
        "-n", "--session", dest="session", type="int", help="number of session."
    )
    parser.add_option(
        "-d",
        "--duration",
        dest="duration",
        type="int",
        default=120,
        help="duration of the recording in seconds.",
    )

    (options, args) = parser.parse_args()
    present(options.subject, options.session, options.duration)


if __name__ == "__main__":
    main()

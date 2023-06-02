#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2022.2.5),
    on March 22, 2023, at 10:57
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

# --- Import packages ---
from psychopy import locale_setup
from psychopy import prefs
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

import psychopy.iohub as io
from psychopy.hardware import keyboard

from time import time
from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG

def present(duration = 300, eeg: EEG = None, save_fn = None, subject = None, session = None):

    # Run 'Before Experiment' code from code_3
    caseVal = 0
    score = 0

    record_duration = np.float32(duration)
    markernames = [100, 110, 200, 210]

    # Ensure that relative paths start from the same directory as this script
    _thisDir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(_thisDir)
    # Store info about the experiment session
    psychopyVersion = '2022.2.5'
    expName = 'feedback3'  # from the Builder filename that created this script
    expInfo = {
        'participant': '',
        'session': '001',
    }
    ## --- Show participant info dialog --
    #dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
    #if dlg.OK == False:
    #    core.quit()  # user pressed cancel
    expInfo['date'] = data.getDateStr()  # add a simple timestamp
    expInfo['expName'] = expName
    expInfo['psychopyVersion'] = psychopyVersion

    if subject == None:
        subject = 0
    if session == None:
        session = 1
    date = data.getDateStr()
    
    # Data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    filename = _thisDir + os.sep + u'data/%s_%s_%s' % (subject, expName, date)

    # An ExperimentHandler isn't essential but helps with data saving
    thisExp = data.ExperimentHandler(name=expName, version='',
        extraInfo=expInfo, runtimeInfo=None,
        originPath='C:\\Users\\eeg-user\\Downloads\\feedback3.py',
        savePickle=True, saveWideText=True,
        dataFileName=filename)
    # save a log file for detail verbose info
    logFile = logging.LogFile(filename+'.log', level=logging.EXP)
    logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

    endExpNow = False  # flag for 'escape' or other condition => quit the exp
    frameTolerance = 0.001  # how close to onset before 'same' frame

    # Start Code - component code to be run after the window creation

    # --- Setup the Window ---
    win = visual.Window(
        size=(1024, 768), fullscr=True, screen=0, 
        winType='pyglet', allowStencil=False,
        monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
        blendMode='avg', useFBO=True, 
        units='height')
    win.mouseVisible = False
    # store frame rate of monitor if we can measure it
    expInfo['frameRate'] = win.getActualFrameRate()
    if expInfo['frameRate'] != None:
        frameDur = 1.0 / round(expInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0  # could not measure, so guess
    # --- Setup input devices ---
    ioConfig = {}

    # Setup iohub keyboard
    ioConfig['Keyboard'] = dict(use_keymap='psychopy')

    ioSession = str(session)
    #if 'session' in expInfo:
    #    ioSession = str(expInfo['session'])
    ioServer = io.launchHubServer(window=win, **ioConfig)
    eyetracker = None

    # create a default keyboard (e.g. to check for escape)
    defaultKeyboard = keyboard.Keyboard()
    
    # --- Initialize components for Routine "precode" ---
    text = visual.TextStim(win=win, name='text',
        text='Introduction\n\nUse Left And Right Arrow Keys To Select an Answer\n\nNumber will be added or subtracted from score\n\nTry score best\n\nPress Space to Begin',
        font='Open Sans',
        pos=(0, 0), height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    key_resp_2 = keyboard.Keyboard()

    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            random_id = random.randint(1000,10000)
            save_fn = generate_save_fn(eeg.device_name, "risk_taking", random_id, random_id, "unnamed")
            print(
                f"No path for a save file was passed to the experiment. Saving data to {save_fn}"
            )
        eeg.start(save_fn, duration=record_duration + 5)
        
    start = time()
    
    # --- Initialize components for Routine "trial" ---
    key_resp = keyboard.Keyboard()
    textbox = visual.TextBox2(
         win, text='', font='Open Sans',
         pos=(0, 0),     letterHeight=0.2,
         size=(None, None), borderWidth=2.0,
         color='white', colorSpace='rgb',
         opacity=None,
         bold=False, italic=False,
         lineSpacing=1.0,
         padding=0.0, alignment='center',
         anchor='center-right',
         fillColor=None, borderColor=None,
         flipHoriz=False, flipVert=False,
         editable=False,
         name='textbox',
         autoLog=True,
    )
    textbox2 = visual.TextBox2(
         win, text='', font='Open Sans',
         pos=(0, 0),     letterHeight=0.2,
         size=(None, None), borderWidth=2.0,
         color='white', colorSpace='rgb',
         opacity=None,
         bold=False, italic=False,
         lineSpacing=1.0,
         padding=0.0, alignment='center',
         anchor='center-left',
         fillColor=None, borderColor=None,
         flipHoriz=False, flipVert=False,
         editable=False,
         name='textbox2',
         autoLog=True,
    )
    scoreboard = visual.TextBox2(
         win, text='', font='Open Sans',
         pos=(0, .3),     letterHeight=0.1,
         size=(None, None), borderWidth=2.0,
         color='yellow', colorSpace='rgb',
         opacity=None,
         bold=False, italic=False,
         lineSpacing=1.0,
         padding=0.0, alignment='center',
         anchor='center',
         fillColor=None, borderColor=None,
         flipHoriz=False, flipVert=False,
         editable=False,
         name='scoreboard',
         autoLog=True,
    )
    textbox_3 = visual.TextBox2(
         win, text='Pick', font='Open Sans',
         pos=(0, 0),     letterHeight=0.09,
         size=(None, None), borderWidth=2.0,
         color='white', colorSpace='rgb',
         opacity=None,
         bold=False, italic=False,
         lineSpacing=1.0,
         padding=0.0, alignment='center',
         anchor='top-center',
         fillColor=None, borderColor=None,
         flipHoriz=False, flipVert=False,
         editable=False,
         name='textbox_3',
         autoLog=True,
    )

    # --- Initialize components for Routine "feedback" ---

    # --- Initialize components for Routine "feedback_2" ---
    txt1 = visual.TextBox2(
         win, text='', font='Open Sans',
         pos=(0, 0),     letterHeight=0.2,
         size=(None, None), borderWidth=2.0,
         color='white', colorSpace='rgb',
         opacity=None,
         bold=False, italic=False,
         lineSpacing=1.0,
         padding=0.0, alignment='center',
         anchor='center-right',
         fillColor=None, borderColor=None,
         flipHoriz=False, flipVert=False,
         editable=False,
         name='txt1',
         autoLog=True,
    )
    txt2 = visual.TextBox2(
         win, text='', font='Open Sans',
         pos=(0, 0),     letterHeight=0.2,
         size=(None, None), borderWidth=2.0,
         color='white', colorSpace='rgb',
         opacity=None,
         bold=False, italic=False,
         lineSpacing=1.0,
         padding=0.0, alignment='center',
         anchor='center-left',
         fillColor=None, borderColor=None,
         flipHoriz=False, flipVert=False,
         editable=False,
         name='txt2',
         autoLog=True,
    )
    textbox_2 = visual.TextBox2(
         win, text='', font='Open Sans',
         pos=(0, .3),     letterHeight=0.1,
         size=(None, None), borderWidth=2.0,
         color='yellow', colorSpace='rgb',
         opacity=None,
         bold=False, italic=False,
         lineSpacing=1.0,
         padding=0.0, alignment='center',
         anchor='center',
         fillColor=None, borderColor=None,
         flipHoriz=False, flipVert=False,
         editable=False,
         name='textbox_2',
         autoLog=True,
    )

    # Create some handy timers
    globalClock = core.Clock()  # to track the time since experiment started
    routineTimer = core.Clock()  # to track time remaining of each (possibly non-slip) routine 

    # --- Prepare to start Routine "precode" ---
    continueRoutine = True
    routineForceEnded = False
    # update component parameters for each repeat
    key_resp_2.keys = []
    key_resp_2.rt = []
    _key_resp_2_allKeys = []
    # keep track of which components have finished
    precodeComponents = [text, key_resp_2]
    for thisComponent in precodeComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1

    # --- Run Routine "precode" ---
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame

        # *text* updates
        if text.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text.frameNStart = frameN  # exact frame index
            text.tStart = t  # local t and not account for scr refresh
            text.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'text.started')
            text.setAutoDraw(True)

        # *key_resp_2* updates
        waitOnFlip = False
        if key_resp_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_2.frameNStart = frameN  # exact frame index
            key_resp_2.tStart = t  # local t and not account for scr refresh
            key_resp_2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_2, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'key_resp_2.started')
            key_resp_2.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_2.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_2.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_2.getKeys(keyList=['space'], waitRelease=False)
            _key_resp_2_allKeys.extend(theseKeys)
            if len(_key_resp_2_allKeys):
                key_resp_2.keys = _key_resp_2_allKeys[-1].name  # just the last key pressed
                key_resp_2.rt = _key_resp_2_allKeys[-1].rt
                # a response ends the routine
                continueRoutine = False

        # check for quit (typically the Esc key)
        if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
            core.quit()

        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in precodeComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished

        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()

    # --- Ending Routine "precode" ---
    for thisComponent in precodeComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # check responses
    if key_resp_2.keys in ['', [], None]:  # No response was made
        key_resp_2.keys = None
    thisExp.addData('key_resp_2.keys',key_resp_2.keys)
    if key_resp_2.keys != None:  # we had a response
        thisExp.addData('key_resp_2.rt', key_resp_2.rt)
    thisExp.nextEntry()
    # the Routine "precode" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()

    # set up handler to look after randomisation of conditions etc
    trials = data.TrialHandler(nReps=10.0, method='random', 
        extraInfo=expInfo, originPath=-1,
        trialList=[None],
        seed=None, name='trials')
    thisExp.addLoop(trials)  # add the loop to the experiment
    thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
    if thisTrial != None:
        for paramName in thisTrial:
            exec('{} = thisTrial[paramName]'.format(paramName))

    for thisTrial in trials:
        currentLoop = trials
        # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
        if thisTrial != None:
            for paramName in thisTrial:
                exec('{} = thisTrial[paramName]'.format(paramName))

        # --- Prepare to start Routine "trial" ---
        continueRoutine = True
        routineForceEnded = False
        # update component parameters for each repeat
        # Run 'Begin Routine' code from code_2
        chance = np.random.randint(0,100)
        leftCorrect = True
        if caseVal == 0:
            num1= np.random.randint(1,10)
            num2 = np.random.randint(15,25)
            marker = 100
            if chance > 70:
                leftCorrect = False
        elif caseVal == 1:
            num1 = 5
            num2 = 5
            marker = 110
            if chance > 50:
                leftCorrect = False
        elif caseVal == 2:
            num1=np.random.randint(20,30)
            num2 = np.random.randint(75,100)
            marker = 200
            if chance > 70:
                leftCorrect = False
        else:
            num1 = 75
            num2 = 75
            marker = 210
            if chance > 50:
                leftCorrect = False
            caseVal = 0

        str1= str(num1)
        str2 = str(num2)
        caseVal += 1
        outText= str1+ "         " + str2

        outScore = "Score: " + str(score)

        key_resp.keys = []
        key_resp.rt = []
        _key_resp_allKeys = []
        textbox.reset()
        textbox.setText(str1)
        textbox2.reset()
        textbox2.setText(str2)
        scoreboard.reset()
        scoreboard.setText(outScore
    )
        textbox_3.reset()
        # keep track of which components have finished
        trialComponents = [key_resp, textbox, textbox2, scoreboard, textbox_3]
        for thisComponent in trialComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1

        # --- Run Routine "trial" ---
        while continueRoutine and routineTimer.getTime() < 3.5:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *key_resp* updates
            waitOnFlip = False
            if key_resp.status == NOT_STARTED and tThisFlip >= 1-frameTolerance:
                # keep track of start time/frame for later
                key_resp.frameNStart = frameN  # exact frame index
                key_resp.tStart = t  # local t and not account for scr refresh
                key_resp.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'key_resp.started')
                key_resp.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(key_resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if key_resp.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > key_resp.tStartRefresh + 2.5-frameTolerance:
                    # keep track of stop time/frame for later
                    key_resp.tStop = t  # not accounting for scr refresh
                    key_resp.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp.stopped')
                    key_resp.status = FINISHED
            if key_resp.status == STARTED and not waitOnFlip:
                theseKeys = key_resp.getKeys(keyList=['1','2','left','right','space'], waitRelease=False)
                _key_resp_allKeys.extend(theseKeys)
                if len(_key_resp_allKeys):
                    key_resp.keys = _key_resp_allKeys[-1].name  # just the last key pressed
                    key_resp.rt = _key_resp_allKeys[-1].rt
                    # a response ends the routine
                    continueRoutine = False

            # *textbox* updates
            if textbox.status == NOT_STARTED and tThisFlip >= .1-frameTolerance:
                # keep track of start time/frame for later
                textbox.frameNStart = frameN  # exact frame index
                textbox.tStart = t  # local t and not account for scr refresh
                textbox.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(textbox, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'textbox.started')
                textbox.setAutoDraw(True)
            if textbox.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > textbox.tStartRefresh + 3.4-frameTolerance:
                    # keep track of stop time/frame for later
                    textbox.tStop = t  # not accounting for scr refresh
                    textbox.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'textbox.stopped')
                    textbox.setAutoDraw(False)

            # *textbox2* updates
            if textbox2.status == NOT_STARTED and tThisFlip >= 0.1-frameTolerance:
                # keep track of start time/frame for later
                textbox2.frameNStart = frameN  # exact frame index
                textbox2.tStart = t  # local t and not account for scr refresh
                textbox2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(textbox2, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'textbox2.started')
                textbox2.setAutoDraw(True)
            if textbox2.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > textbox2.tStartRefresh + 3.4-frameTolerance:
                    # keep track of stop time/frame for later
                    textbox2.tStop = t  # not accounting for scr refresh
                    textbox2.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'textbox2.stopped')
                    textbox2.setAutoDraw(False)

            # *scoreboard* updates
            if scoreboard.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                scoreboard.frameNStart = frameN  # exact frame index
                scoreboard.tStart = t  # local t and not account for scr refresh
                scoreboard.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(scoreboard, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'scoreboard.started')
                scoreboard.setAutoDraw(True)
            if scoreboard.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > scoreboard.tStartRefresh + 3.5-frameTolerance:
                    # keep track of stop time/frame for later
                    scoreboard.tStop = t  # not accounting for scr refresh
                    scoreboard.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'scoreboard.stopped')
                    scoreboard.setAutoDraw(False)

            # *textbox_3* updates
            if textbox_3.status == NOT_STARTED and tThisFlip >= 1-frameTolerance:
                # keep track of start time/frame for later
                textbox_3.frameNStart = frameN  # exact frame index
                textbox_3.tStart = t  # local t and not account for scr refresh
                textbox_3.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(textbox_3, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'textbox_3.started')
                textbox_3.setAutoDraw(True)
            if textbox_3.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > textbox_3.tStartRefresh + 2.5-frameTolerance:
                    # keep track of stop time/frame for later
                    textbox_3.tStop = t  # not accounting for scr refresh
                    textbox_3.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'textbox_3.stopped')
                    textbox_3.setAutoDraw(False)

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in trialComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
                # Push sample
                if eeg:
                    if frameN == 0:
                        timestamp = time()
                        eeg.push_sample(marker=marker, timestamp=timestamp)

        # --- Ending Routine "trial" ---
        for thisComponent in trialComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # check responses
        if key_resp.keys in ['', [], None]:  # No response was made
            key_resp.keys = None
        trials.addData('key_resp.keys',key_resp.keys)
        if key_resp.keys != None:  # we had a response
            trials.addData('key_resp.rt', key_resp.rt)
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if routineForceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-3.500000)

        # --- Prepare to start Routine "feedback" ---
        continueRoutine = True
        routineForceEnded = False
        # update component parameters for each repeat
        # Run 'Begin Routine' code from code
        msg = ""
        test = str(key_resp.keys[0])
        if leftCorrect == True:
            if key_resp.keys[0] == '1' or key_resp.keys[0]=='l':
                score += num1
		marker = 3
            elif key_resp.keys[0] == '2'or key_resp.keys[0]=='r':
                score -= num2
		marker = 4
            else:
                score -= 25
		marker = 5
        else:
            if key_resp.keys[0] == '1' or key_resp.keys[0]=='l':
                score -= num1
		marker = 4
            elif key_resp.keys[0] == '2'or key_resp.keys[0]=='r':
                score += num2
		marker = 3
            else:
                score -= 25
            	marker = 5

        # Run 'Begin Routine' code from code_4
        if leftCorrect == True:
            text1Color = "lime"
            text2Color = "red"
        else:
            text1Color = "red"
            text2Color = "lime"

        outScore2 = "Score: " + str(score)
        # keep track of which components have finished
        feedbackComponents = []
        for thisComponent in feedbackComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1

        # --- Run Routine "feedback" ---
        while continueRoutine:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in feedbackComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()

        # --- Ending Routine "feedback" ---
        for thisComponent in feedbackComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # the Routine "feedback" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()

        # --- Prepare to start Routine "feedback_2" ---
        continueRoutine = True
        routineForceEnded = False
        # update component parameters for each repeat
        txt1.reset()
        txt1.setColor(text1Color, colorSpace='rgb')
        txt2.reset()
        txt2.setColor(text2Color, colorSpace='rgb')
        textbox_2.reset()
        textbox_2.setText(outScore2)
        # keep track of which components have finished
        feedback_2Components = [txt1, txt2, textbox_2]
        for thisComponent in feedback_2Components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1

        # --- Run Routine "feedback_2" ---
        while continueRoutine and routineTimer.getTime() < 3.5:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame

            # *txt1* updates
            if txt1.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                # keep track of start time/frame for later
                txt1.frameNStart = frameN  # exact frame index
                txt1.tStart = t  # local t and not account for scr refresh
                txt1.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(txt1, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'txt1.started')
                txt1.setAutoDraw(True)
            if txt1.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > txt1.tStartRefresh + 3-frameTolerance:
                    # keep track of stop time/frame for later
                    txt1.tStop = t  # not accounting for scr refresh
                    txt1.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'txt1.stopped')
                    txt1.setAutoDraw(False)
            if txt1.status == STARTED:  # only update if drawing
                txt1.setText(num1
    , log=False)

            # *txt2* updates
            if txt2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                # keep track of start time/frame for later
                txt2.frameNStart = frameN  # exact frame index
                txt2.tStart = t  # local t and not account for scr refresh
                txt2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(txt2, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'txt2.started')
                txt2.setAutoDraw(True)
            if txt2.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > txt2.tStartRefresh + 3-frameTolerance:
                    # keep track of stop time/frame for later
                    txt2.tStop = t  # not accounting for scr refresh
                    txt2.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'txt2.stopped')
                    txt2.setAutoDraw(False)
            if txt2.status == STARTED:  # only update if drawing
                txt2.setText(num2, log=False)

            # *textbox_2* updates
            if textbox_2.status == NOT_STARTED and tThisFlip >= 0.5-frameTolerance:
                # keep track of start time/frame for later
                textbox_2.frameNStart = frameN  # exact frame index
                textbox_2.tStart = t  # local t and not account for scr refresh
                textbox_2.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(textbox_2, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'textbox_2.started')
                textbox_2.setAutoDraw(True)
            if textbox_2.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > textbox_2.tStartRefresh + 3-frameTolerance:
                    # keep track of stop time/frame for later
                    textbox_2.tStop = t  # not accounting for scr refresh
                    textbox_2.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'textbox_2.stopped')
                    textbox_2.setAutoDraw(False)

            # check for quit (typically the Esc key)
            if endExpNow or defaultKeyboard.getKeys(keyList=["escape"]):
                core.quit()

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in feedback_2Components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
                
                if eeg:
                    if frameN == 0:
                        timestamp = time()
                        eeg.push_sample(marker=marker, timestamp=timestamp)

        # --- Ending Routine "feedback_2" ---
        for thisComponent in feedback_2Components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if routineForceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-3.500000)
        thisExp.nextEntry()

    # completed 10.0 repeats of 'trials'


    # --- End experiment ---
    # Flip one final time so any remaining win.callOnFlip() 
    # and win.timeOnFlip() tasks get executed before quitting
    win.flip()
    # Cleanup
    if eeg:
        eeg.stop()

    # these shouldn't be strictly necessary (should auto-save)
    thisExp.saveAsWideText(filename+'.csv', delim='auto')
    thisExp.saveAsPickle(filename)
    logging.flush()
    # make sure everything is closed down
    if eyetracker:
        eyetracker.setConnectionState(False)
    thisExp.abort()  # or data files will save again on exit
    win.close()
    core.quit()

import os
from time import time
from glob import glob
from random import choice
import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event
from eegnb import generate_save_fn
from final_project.stimuli import CONTROL, EXP
__title__ = "Political Emotions Experiment"

def present(duration=120, eeg=None, save_fn=None, ver=1):
    n_trials = 75
    iti = 0.5
    soa = 0.5
    jitter = 0.2
    record_duration = np.float32(duration)
    markernames = [1, 2, 3]
    num_targets = 0
    
    # Setup trial list
    #image_type is an array of yes or no
    image_type = np.random.randint(3, size=n_trials)
    trials = DataFrame(dict(image_type=image_type,
    timestamp=np.zeros(n_trials)))
    
    def load_image(fn):
        return visual.ImageStim(win=mywin, image=fn)
    
    # Setup graphics
    mywin = visual.Window([1600, 900], color=[1,1,1],
    monitor="testMonitor", units="deg", fullscr=True)
    mywin.flip()
    mywin.flip()
    
    if ver == 1:
    #Control trial
    #left = disgust
    #right = happy
        neutral = list(map(load_image, glob(os.path.join(CONTROL,"Neutral_*"))))
        left = list(map(load_image, glob(os.path.join(CONTROL,"Disgust_*"))))
        right = list(map(load_image, glob(os.path.join(CONTROL,"Happy_*"))))
    elif ver == 2:
    #Experimental trial
    #left = dem
    #right = rep
        neutral = list(map(load_image,glob(os.path.join(EXP,"Ind_*"))))
        left = list(map(load_image, glob(os.path.join(EXP,"Dem_*"))))
        right = list(map(load_image,glob(os.path.join(EXP,"Rep_*"))))
    stim = [right, left, neutral]
    
    # Show instructions
    show_instructions(duration=duration)
    
    # start the EEG stream, will delay 5 seconds to let signal settle
    if eeg:
        if save_fn is None: # If no save_fn passed, generate a new unnamed save file
        save_fn = generate_save_fn(eeg.device_name,"visual_p300", "unnamed")
        print(f"No path for a save file was passed to the experiment. Saving data to {save_fn}")
        eeg.start(save_fn, duration=record_duration)
    
    # Iterate through the events
    start = time()
    
    for ii, trial in trials.iterrows():
        
        # Inter trial interval
        core.wait(iti + np.random.rand() * jitter)
        
        # Select and display image
        label = trials["image_type"].iloc[ii]
        if label == 2:
            image = choice(neutral)
        elif label == 0:
            image = choice(right)
        else:
            image = choice(left)
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
        
        # offset
        core.wait(soa)
        mywin.flip()
        
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break
        
        event.clearEvents()
        
    # Goodbye Screen
    text = visual.TextStim(win=mywin, text = "Thank you for participating. Press spacebar to exit the experiment.",
        color=[-1, -1, -1],pos=[0, 5],)
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
    Welcome to the Political Emotions experiment!
    Stay still, focus on the center of the screen, and try not to blink.
    This block will run for %s seconds.
    Press spacebar to continue.
    """
    instruction_text = instruction_text % duration
    
    # graphics
    mywin = visual.Window([1600, 900], color=[1,1,1],
    monitor="testMonitor", units="deg", fullscr=True)
    mywin.mouseVisible = False
    mywin.flip()
    mywin.flip()
    
    # Instructions
    text = visual.TextStim(win=mywin, text=instruction_text,color=[-1, -1, -1])
    text.draw()
    mywin.flip()
    event.waitKeys(keyList="space")
    mywin.mouseVisible = True
    mywin.close()
import numpy as np
from pandas import DataFrame
from psychopy import visual, core, event
from time import time, strftime, gmtime
from optparse import OptionParser
from pylsl import StreamInfo, StreamOutlet

from eegnb import generate_save_fn
from eegnb.devices.eeg import EEG


def present(duration=120, eeg: EEG=None, save_fn=None):

    # create
    info = StreamInfo("Markers", "Markers", 1, 0, "int32", "myuidw43536")

    # next make an outlet
    outlet = StreamOutlet(info)

    markernames = [1, 2]

    start = time()

    n_trials = 2000
    iti = 0.2
    jitter = 0.1
    soa = 0.2
    record_duration = np.float32(duration)

    # Setup log
    position = np.random.randint(0, 2, n_trials)
    trials = DataFrame(dict(position=position, timestamp=np.zeros(n_trials)))

    # graphics
    mywin = visual.Window(
        [1920, 1080], monitor="testMonitor", units="deg", fullscr=True
    )
    grating = visual.GratingStim(win=mywin, mask="circle", size=20, sf=4)
    fixation = visual.GratingStim(win=mywin, size=0.2, pos=[0, 0], sf=0, rgb=[1, 0, 0])

    if eeg:
        if save_fn is None:  # If no save_fn passed, generate a new unnamed save file
            random_id = random.randint(1000,10000)
            save_fn = generate_save_fn(eeg.device_name, "visual_vep", random_id, random_id, "unnamed")
            print(
                f"No path for a save file was passed to the experiment. Saving data to {save_fn}"
            )
        eeg.start(save_fn, duration=record_duration + 5)
    
    # Start EEG Stream, wait for signal to settle, and then pull timestamp for start point
    start = time()
    
    for ii, trial in trials.iterrows():
        # inter trial interval
        core.wait(iti + np.random.rand() * jitter)

        # onset
        grating.phase += np.random.rand()
        pos = trials["position"].iloc[ii]
        grating.pos = [25 * (pos - 0.5), 0]
        grating.draw()
        fixation.draw()
        
        # Push sample
        if eeg:
            timestamp = time()
            if eeg.backend == "muselsl":
                marker = [markernames[pos]]
            else:
                marker = markernames[pos]
            eeg.push_sample(marker=marker, timestamp=timestamp)
            
        mywin.flip()

        # offset
        core.wait(soa)
        fixation.draw()
        mywin.flip()
        if len(event.getKeys()) > 0 or (time() - start) > record_duration:
            break
        event.clearEvents()
    
    # Cleanup
    if eeg:
        eeg.stop()
        
    mywin.close()


def main():
    parser = OptionParser()

    parser.add_option(
        "-d",
        "--duration",
        dest="duration",
        type="int",
        default=120,
        help="duration of the recording in seconds.",
    )

    (options, args) = parser.parse_args()
    present(options.duration)


if __name__ == "__main__":
    main()

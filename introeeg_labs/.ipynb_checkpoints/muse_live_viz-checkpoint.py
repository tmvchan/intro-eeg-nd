import os
import time
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime
from collections import deque
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import DataFilter, DetrendOperations

# =============================================
# === CONFIG ===
# =============================================
BoardId             = BoardIds.MUSE_2_BOARD
sfreq               = 256
UPDATE_INTERVAL_SEC = 0.2          # Seconds between updates
HISTORY_SEC         = 60           # How many seconds to show on graph
channel_names       = ['TP9', 'AF7', 'AF8', 'TP10']
CSV_FILE            = 'muse_realtime.csv'
# =============================================

window_size  = int(sfreq * UPDATE_INTERVAL_SEC)
history_len  = int(HISTORY_SEC / UPDATE_INTERVAL_SEC)

# Pre-compute FFT indices
fft_freqs = np.fft.rfftfreq(window_size, 1.0 / sfreq)
alpha_idx = np.where((fft_freqs >= 8.0)  & (fft_freqs <= 12.0))[0]
beta_idx  = np.where((fft_freqs >= 13.0) & (fft_freqs <= 30.0))[0]

# Circular buffers for EEG data
eeg_buffers = [deque(maxlen=window_size) for _ in range(4)]

# Shared history for plotting (thread-safe via lock)
lock = threading.Lock()
time_history   = deque(maxlen=history_len)
alpha_history  = deque(maxlen=history_len)
beta_history   = deque(maxlen=history_len)
ratio_history  = deque(maxlen=history_len)

# =============================================
# === BrainFlow thread ===
# =============================================
def brainflow_thread():
    params = BrainFlowInputParams()
    params.serial_port = ''
    board = BoardShim(BoardId, params)
    board.prepare_session()
    board.start_stream()
    print(f"Connected! Interval: {UPDATE_INTERVAL_SEC}s | Window: {window_size} samples")

    try:
        csv_header = True
        last_update = time.time()
        sample_num = 0

        while True:
            data = board.get_board_data()
            if data.shape[1] > 0:
                eeg_channels = BoardShim.get_eeg_channels(BoardId)
                for s in range(data.shape[1]):
                    for ch in range(4):
                        eeg_buffers[ch].append(data[eeg_channels[ch], s])

            now = time.time()
            if now - last_update < UPDATE_INTERVAL_SEC:
                time.sleep(0.01)
                continue

            if len(eeg_buffers[0]) < window_size:
                last_update = now
                continue

            last_update = now
            sample_num += 1

            # Build window
            eeg_window = np.array([list(buf) for buf in eeg_buffers], dtype=np.float64).T
            for ch in range(4):
                DataFilter.detrend(eeg_window[:, ch], DetrendOperations.LINEAR.value)

            # FFT → bands
            band_powers = np.zeros((4, 2))
            for ch in range(4):
                fft_vals = np.fft.rfft(eeg_window[:, ch])
                psd = (np.abs(fft_vals) ** 2) / window_size
                band_powers[ch, 0] = np.mean(psd[alpha_idx])
                band_powers[ch, 1] = np.mean(psd[beta_idx])

            alpha_mean = np.mean(band_powers[:, 0])
            beta_mean  = np.mean(band_powers[:, 1])
            ratio      = beta_mean / alpha_mean if alpha_mean > 0 else 0
            state      = 'RELAX' if ratio < 0.7 else 'FOCUS' if ratio > 1.2 else 'BALANCED'
            ts         = datetime.now().strftime('%H:%M:%S')

            # Push to plot history
            with lock:
                time_history.append(sample_num)
                alpha_history.append(alpha_mean)
                beta_history.append(beta_mean)
                ratio_history.append(ratio)

            # Terminal
            line = f"{ts} ({UPDATE_INTERVAL_SEC}s) | "
            for i, ch_name in enumerate(channel_names):
                line += f"{ch_name} a={band_powers[i,0]:.2f} b={band_powers[i,1]:.2f}  "
            line += f"| a={alpha_mean:.2f} b={beta_mean:.2f} b/a={ratio:.2f} [{state}]"
            width = os.get_terminal_size().columns
            print(f"\r{' ' * width}\r{line}", end='', flush=True)

            # CSV
            row = {
                'ts': ts,
                'interval_sec': UPDATE_INTERVAL_SEC,
                **{f'{ch}_alpha': band_powers[i, 0] for i, ch in enumerate(channel_names)},
                **{f'{ch}_beta':  band_powers[i, 1] for i, ch in enumerate(channel_names)},
                'alpha_mean': alpha_mean,
                'beta_mean':  beta_mean,
                'ratio':      ratio,
                'state':      state
            }
            pd.DataFrame([row]).to_csv(CSV_FILE, mode='a', header=csv_header, index=False)
            csv_header = False

    finally:
        board.stop_stream()
        board.release_session()

# =============================================
# === Matplotlib live graph ===
# =============================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
fig.suptitle('Muse 2 Live EEG Band Power', fontsize=14, fontweight='bold')

line_alpha, = ax1.plot([], [], label='Alpha (8-12Hz)', color='royalblue', linewidth=2)
line_beta,  = ax1.plot([], [], label='Beta (13-30Hz)',  color='tomato',    linewidth=2)
line_ratio, = ax2.plot([], [], label='β/α Ratio',      color='mediumseagreen', linewidth=2)
ax2.axhline(y=0.7,  color='royalblue', linestyle='--', alpha=0.5, label='Relax threshold')
ax2.axhline(y=1.2,  color='tomato',    linestyle='--', alpha=0.5, label='Focus threshold')

ax1.set_ylabel('Band Power (µV²)')
ax1.legend(loc='upper right')
ax1.set_title('Mean Alpha & Beta Power')
ax1.grid(True, alpha=0.3)

ax2.set_ylabel('β/α Ratio')
ax2.set_xlabel(f'Time (updates, 1 update = {UPDATE_INTERVAL_SEC}s)')
ax2.legend(loc='upper right')
ax2.set_title('Focus vs Relax Ratio  (>1.2 = Focus | <0.7 = Relax)')
ax2.grid(True, alpha=0.3)
ax2.set_ylim(0, 2.0)

state_text = ax2.text(0.01, 0.85, '', transform=ax2.transAxes,
                      fontsize=13, fontweight='bold', color='purple')

def animate(_):
    with lock:
        if len(time_history) < 2:
            return line_alpha, line_beta, line_ratio, state_text
        t  = list(time_history)
        a  = list(alpha_history)
        b  = list(beta_history)
        r  = list(ratio_history)

    line_alpha.set_data(t, a)
    line_beta.set_data(t, b)
    line_ratio.set_data(t, r)

    ax1.set_xlim(max(0, t[-1] - history_len), t[-1] + 1)
    ax1.set_ylim(0, max(max(a), max(b)) * 1.2 + 1)
    ax2.set_xlim(max(0, t[-1] - history_len), t[-1] + 1)
    ax2.set_ylim(0, 2.0)

    ratio_now = r[-1]
    state_now = 'RELAX' if ratio_now < 0.7 else 'FOCUS' if ratio_now > 1.2 else 'BALANCED'
    state_text.set_text(f'State: {state_now}  (β/α={ratio_now:.2f})')

    return line_alpha, line_beta, line_ratio, state_text

# Start BrainFlow in background thread
t = threading.Thread(target=brainflow_thread, daemon=True)
t.start()

# Start animation on main thread (required for matplotlib on Windows)
ani = animation.FuncAnimation(fig, animate, interval=int(UPDATE_INTERVAL_SEC * 1000), blit=True)
plt.tight_layout()
plt.show()

print("\nDone. Data saved to", CSV_FILE)

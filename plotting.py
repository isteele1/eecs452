
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import deque
import time

def stft(x, window, stride):
    time_length = int((list_length - len(window))/stride) + 1
    X = np.zeros((len(window) // 2, time_length), dtype=np.float64)
    for i in range(0, time_length):
        data = x[i * stride:i * stride + len(window)]
        freq_data = np.abs(np.fft.fft(data * window, len(window)))
        freq_data[freq_data == 0] = 1e-10
        freq_data = freq_data[:len(freq_data) // 2]
        X[:, i] = 20 * np.log10(freq_data)
    return X

# Settings
port_name = "/dev/tty.usbmodem1103"  # Must be changed if port changes
plotting_rate = 25  # in ms
fs = 1 / (plotting_rate / 1000)
list_length = int(10000 / plotting_rate)  # 10 seconds of data

# STFT settings
N = 40
L = 40
mean_thresh = 500
high_power_threshold = 1200

spec_length = int((list_length - N)/L) + 1  # Width of spectrogram
freq_rate = plotting_rate * (list_length / spec_length)
halt = False
ser = serial.Serial(port_name, 115200, timeout=1)

# Initialize arrays of data
t = np.linspace(-10, 0, spec_length)
f = np.linspace(0, fs/2, int(N/2))
raw_data = deque([1.0E-10]*list_length, maxlen=list_length)
processed_data = deque([1.0E-10]*list_length, maxlen=list_length)
power_values = deque([1.0E-10]*list_length, maxlen=list_length)
attack_labels = deque(["none"] * list_length)

last_segment = {'start': None, 'end': None, 'type': None}
highlight_patches = []

rect = np.ones(N)

# stft_matrix = stft(list(raw_data), hamm, L)
stft_matrix = np.ones((int(N/2), spec_length))

timestamps = np.linspace(-10, 0, list_length).tolist()

jam_detect = False
spoof_detect = False

# Define detection parameters
jam_drop_threshold = -8           # cm drop
jam_stability_var_threshold = 0.5  # cm^2
spoof_var_threshold = 12           # cm^2
spoof_power_threshold = 400        # total spectral power
detection_window = 25              # number of samples (~0.25s)
trigger_cooldown = 2.4             # seconds

# Global state
last_trigger_time = {'jamming': 0, 'spoofing': 0}

attack_regions = []  # List of (start_idx, end_idx, type)
current_attack = None
current_start_idx = None
attack_type = "none"

# Declare plots and axes for each figure
fig1, ax1 = plt.subplots(figsize=(8, 8))
line1, = ax1.plot([], [], label="Raw Data")
line2, = ax1.plot([], [], label="Holt EMA Data")
ax1.set_xlim(-10, 0)
ax1.set_ylim(0, 100)
ax1.legend(loc="upper left")
ax1.set_xlabel("Time (sec)")
ax1.set_ylabel("Distance (cm)")

fig2, ax2 = plt.subplots(figsize=(8, 8))
quadmesh = ax2.pcolormesh(t, f, np.zeros((len(f), len(t))), shading='gouraud', cmap='inferno', vmin=-25, vmax=60)
ax2.title.set_text("Log-Amplitude Spectrogram")
ax2.set_xlabel("Time (sec, 0 = most recent sample)")
ax2.set_ylabel("Frequency (Hz)")

fig3, ax3 = plt.subplots(figsize=(8, 8))
line3, = ax3.plot([], [])
# ax3.axhline(y=high_power_threshold, color='red', linestyle='--', label="High Threshold")
ax3.set_xlim(-10, 0)
ax3.set_ylim(0, 2000)
ax3.set_xlabel("Time (sec, 0 = most recent sample)")
ax3.set_ylabel("Total Power")
ax3.set_title("Spectral Power")

# Initialize Plot Functions
def init1():
    line1.set_data([], [])
    line2.set_data([], [])
    return line1, line2

def init2():
    quadmesh.set_array(np.zeros((len(f), len(t))))  # -1 because pcolormesh grid is 1 less than shape
    return quadmesh,

def init3():
    line3.set_data([], [])
    return line3,

# Update Plot Functions
def update1(frame):
    global stft_matrix, jam_detect, spoof_detect
    str = ser.readline().decode('utf-8').strip()
    a_str, b_str = str.split()
    raw_val = float(a_str)
    processed_val = float(b_str)

    str2 = ser.readline().decode().strip()
    stft_array = np.fromstring(str2, dtype=float, sep=' ')
    stft_matrix = np.roll(stft_matrix, -1, axis=1)
    stft_matrix[:, -1] = stft_array

    if str and not halt:
        raw_data.append(raw_val)
        line1.set_data(timestamps, list(raw_data))
        processed_data.append(processed_val)
        line2.set_data(timestamps, list(processed_data))
        if jam_detect:
            ax1.set_title("Attack Type: Jamming")
        elif spoof_detect:
            ax1.set_title("Attack Type: Spoofing")
        else:
            ax1.set_title("No Attack")

    # highlight_recent_attack(ax1, timestamps, min_segment_length=10)

    return line1, line2, ax1.title

def update2(frame):
    global stft_matrix
    if not halt:
        # print("Min STFT value: ", np.min(stft_matrix))
        # print("Max STFT value: ", np.max(stft_matrix))
        quadmesh.set_array(stft_matrix.ravel())  # Match the shape expected by pcolormesh
    return quadmesh,

def update3(frame):
    global stft_matrix, current_attack, current_start_idx, attack_regions, attack_type
    global jam_detect, spoof_detect
    if not halt:
        new_value = np.sum(stft_matrix[:, -1])
        if new_value < 0:
            new_value = 0
        power_values.append(new_value)
        line3.set_data(timestamps, list(power_values))

    check_conditions()
    return line3,

def check_conditions():
    global jam_detect, spoof_detect, attack_type, last_trigger_time

    now = time.time()
    dist_window = np.array(raw_data)[-detection_window:]
    power_window = np.array(power_values)[-5:]

    first_derivative = np.diff(dist_window)
    derivative_range = np.max(first_derivative) - np.min(first_derivative)

    # Typical difference between jammed distance and sensed distance, plus some buffer
    jam_spoof_threshold = 80
    
    delta = dist_window[len(dist_window) - 1] - dist_window[len(dist_window) - 2]
    var = np.var(dist_window)
    jam_var = np.var(dist_window[-10:])

    avg_power = np.mean(power_window)
    # print("Delta:",delta)
    # print("Derivative Range:",derivative_range)

    # print("Variance:", var)
    # print("Derivative Range:",derivative_range)

    # JAMMING detection
    if not spoof_detect:
        if not jam_detect:
            if delta < jam_drop_threshold and derivative_range < jam_spoof_threshold and (now - last_trigger_time['jamming'] > trigger_cooldown):
                jam_detect = True
                last_trigger_time['jamming'] = now
        elif jam_var < jam_stability_var_threshold and now - last_trigger_time['jamming'] > trigger_cooldown:
            jam_detect = True
        elif now - last_trigger_time['jamming'] > trigger_cooldown:
            jam_detect = False

    # SPOOFING detection
    # Increase derivative range if operation at long distance isn't working
    # Jamming should create a derivative range about half of spoofing, adjust this at the expo
    if not jam_detect:
        if not spoof_detect:
            if var > spoof_var_threshold and jam_spoof_threshold < derivative_range < 2*jam_spoof_threshold and (now - last_trigger_time['spoofing'] > trigger_cooldown):
                spoof_detect = True
                last_trigger_time['spoofing'] = now
        elif avg_power > spoof_power_threshold and now - last_trigger_time['spoofing'] > trigger_cooldown:
            spoof_detect = True
        elif now - last_trigger_time['spoofing'] > trigger_cooldown:
            spoof_detect = False

    if derivative_range > 1000:
        print("Data may be corrupted or fluctuating too quickly")

    # Update attack type
    if jam_detect:
        attack_type = "jamming"
    elif spoof_detect:
        attack_type = "spoofing"
    else:
        attack_type = "none"
    # attack_labels.append(attack_type)
    # print(attack_type)

# def highlight_recent_attack(ax, timestamps, min_segment_length=10):
#     global attack_labels, last_segment, highlight_patches

#     # Remove previous patches
#     for patch in highlight_patches:
#         patch.remove()
#     highlight_patches.clear()

#     # Look backward for the most recent consistent attack segment
#     current_val = attack_labels[-1]
#     if current_val == 0:
#         last_segment = {'start': None, 'end': None, 'type': None}
#         return

#     # Find contiguous segment of same attack type
#     count = 1
#     for i in range(len(attack_labels) - 2, -1, -1):
#         if attack_labels[i] == current_val:
#             count += 1
#         else:
#             break

#     if count >= min_segment_length:
#         start_idx = len(attack_labels) - count
#         end_idx = len(attack_labels) - 1
#         start_time = timestamps[start_idx]
#         end_time = timestamps[end_idx]

#         if (last_segment['start'], last_segment['end'], last_segment['type']) != (start_time, end_time, current_val):
#             color = 'orange' if current_val == 1 else 'red'
#             patch = ax.axvspan(start_time, end_time, color=color, alpha=0.2)
#             highlight_patches.append(patch)
#             last_segment = {'start': start_time, 'end': end_time, 'type': current_val}

# Handle keypress events
def on_key(event):
    global halt
    if event.key == 'q':  # Press 'q' to quit
        plt.close('all')
    elif event.key == 'p':  # Press 'p' to pause/unpause plot updates
        halt = not halt

# Main
fig1.canvas.mpl_connect('key_press_event', on_key)
fig2.canvas.mpl_connect('key_press_event', on_key)
fig3.canvas.mpl_connect('key_press_event', on_key)

ani1 = animation.FuncAnimation(fig1, update1, init_func=init1, blit=False, interval=plotting_rate)
ani2 = animation.FuncAnimation(fig2, update2, init_func=init2, blit=True, interval=plotting_rate)
ani3 = animation.FuncAnimation(fig3, update3, init_func=init3, blit=True, interval=plotting_rate)

plt.show()
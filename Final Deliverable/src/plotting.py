# Import libraries
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from collections import deque
import time

### stft()
### Custom Short-Time Fourier Transform function
### -------------------------
# x:        np.array of data
# window:   np.array of window coefficients
# stride:   integer of hop length between data windows taken
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
port_name = "/dev/tty.usbmodem1103" # Must be changed to port name used to connect STM
plotting_rate = 25 # in ms
fs = 1 / (plotting_rate / 1000) # Sampling frequency, in Hz
list_length = int(10000 / plotting_rate) # 10 seconds of data

# Window length and stride length for STFT
N = 40
L = 40

# Initialize spectrogram axes and matrix
spec_length = int((list_length - N)/L) + 1 # Time resoluton of spectrogram
rect = np.ones(N) # Window
stft_matrix = np.ones((int(N/2), spec_length)) # Ones matrix

ser = serial.Serial(port_name, 115200, timeout=1)

# Initialize arrays for plot axes
timestamps = np.linspace(-10, 0, list_length).tolist()
t = np.linspace(-10, 0, spec_length)
f = np.linspace(0, fs/2, int(N/2))

# Initialize data arrays
raw_data = deque([1.0E-10]*list_length, maxlen=list_length)
processed_data = deque([1.0E-10]*list_length, maxlen=list_length)
power_values = deque([1.0E-10]*list_length, maxlen=list_length)
attack_labels = deque(["none"] * list_length)

# Globals to pause plotting and check attacks
halt = False
jam_detect = False
spoof_detect = False

# Define detection parameters
jam_drop_threshold = -8            # drop distance, cm
jam_stability_var_threshold = 0.5  # variance, cm^2
spoof_var_threshold = 12           # variance, cm^2
spoof_power_threshold = 400        # total power
detection_window = 25              # number of samples (~0.25s)
trigger_cooldown = 2.4             # seconds until secondary attack check

# Global state
last_trigger_time = {'jamming': 0, 'spoofing': 0}
attack_type = "none"

# Declare plots and axes for figure 1
fig1, ax1 = plt.subplots(figsize=(8, 8))
line1, = ax1.plot([], [], label="Raw Data")
line2, = ax1.plot([], [], label="Holt EMA Data")
ax1.set_xlim(-10, 0)
ax1.set_ylim(0, 100)
ax1.legend(loc="upper left")
ax1.set_xlabel("Time (sec)")
ax1.set_ylabel("Distance (cm)")

# Declare plots and axes for figure 2
fig2, ax2 = plt.subplots(figsize=(8, 8))
quadmesh = ax2.pcolormesh(t, f, np.zeros((len(f), len(t))), shading='gouraud', cmap='inferno', vmin=-25, vmax=60)
ax2.title.set_text("Log-Amplitude Spectrogram")
ax2.set_xlabel("Time (sec, 0 = most recent sample)")
ax2.set_ylabel("Frequency (Hz)")

# Declare plots and axes for figure 3
fig3, ax3 = plt.subplots(figsize=(8, 8))
line3, = ax3.plot([], [])
ax3.set_xlim(-10, 0)
ax3.set_ylim(0, 2000)
ax3.set_xlabel("Time (sec, 0 = most recent sample)")
ax3.set_ylabel("Total Power")
ax3.set_title("Spectral Power")

# Initialize plot 1
def init1():
    line1.set_data([], [])
    line2.set_data([], [])
    return line1, line2

# Initialize plot 2
def init2():
    quadmesh.set_array(np.zeros((len(f), len(t))))
    return quadmesh,

# Initialize plot 3
def init3():
    line3.set_data([], [])
    return line3,

# Update plot 1
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
    return line1, line2, ax1.title

# Update plot 2
def update2(frame):
    global stft_matrix
    if not halt:
        quadmesh.set_array(stft_matrix.ravel())
    return quadmesh,

# Update plot 3
def update3(frame):
    global stft_matrix, attack_type
    global jam_detect, spoof_detect
    if not halt:
        new_value = np.sum(stft_matrix[:, -1])
        if new_value < 0:
            new_value = 0
        power_values.append(new_value)
        line3.set_data(timestamps, list(power_values))

    check_conditions()
    return line3,

# Check for jamming and spoofing and update global checks
def check_conditions():
    global jam_detect, spoof_detect, attack_type, last_trigger_time

    now = time.time()

    dist_window = np.array(raw_data)[-detection_window:]
    power_window = np.array(power_values)[-5:]
    avg_power = np.mean(power_window)

    first_derivative = np.diff(dist_window)
    derivative_range = np.max(first_derivative) - np.min(first_derivative)

    jam_spoof_threshold = 80
    
    jam_drop = dist_window[len(dist_window) - 1] - dist_window[len(dist_window) - 2]
    spoof_var = np.var(dist_window)
    jam_var = np.var(dist_window[-10:])

    # JAMMING detection
    if not spoof_detect:
        if not jam_detect:
            if jam_drop < jam_drop_threshold and derivative_range < jam_spoof_threshold and (now - last_trigger_time['jamming'] > trigger_cooldown):
                jam_detect = True
                last_trigger_time['jamming'] = now
        elif jam_var < jam_stability_var_threshold and now - last_trigger_time['jamming'] > trigger_cooldown:
            jam_detect = True
        elif now - last_trigger_time['jamming'] > trigger_cooldown:
            jam_detect = False

    # SPOOFING detection
    if not jam_detect:
        if not spoof_detect:
            if spoof_var > spoof_var_threshold and jam_spoof_threshold < derivative_range < 2*jam_spoof_threshold and (now - last_trigger_time['spoofing'] > trigger_cooldown):
                spoof_detect = True
                last_trigger_time['spoofing'] = now
        elif avg_power > spoof_power_threshold and now - last_trigger_time['spoofing'] > trigger_cooldown:
            spoof_detect = True
        elif now - last_trigger_time['spoofing'] > trigger_cooldown:
            spoof_detect = False

    # Update attack type
    if jam_detect:
        attack_type = "jamming"
    elif spoof_detect:
        attack_type = "spoofing"
    else:
        attack_type = "none"

# Handle keypress events
def on_key(event):
    global halt
    if event.key == 'q':    # Press 'q' to quit
        plt.close('all')
    elif event.key == 'p':  # Press 'p' to pause/unpause plot updates
        halt = not halt

# Run keypress commands and animation updates for all plots
fig1.canvas.mpl_connect('key_press_event', on_key)
fig2.canvas.mpl_connect('key_press_event', on_key)
fig3.canvas.mpl_connect('key_press_event', on_key)

ani1 = animation.FuncAnimation(fig1, update1, init_func=init1, blit=False, interval=plotting_rate)
ani2 = animation.FuncAnimation(fig2, update2, init_func=init2, blit=True, interval=plotting_rate)
ani3 = animation.FuncAnimation(fig3, update3, init_func=init3, blit=True, interval=plotting_rate)

plt.show()
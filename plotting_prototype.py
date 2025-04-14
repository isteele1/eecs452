# Plotting function to run on a PC as a demonstration
# Takes in a single string of "raw_data" as a float

import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from spoofing import HoltEMA
import time

# Settings
port_name = "/dev/tty.usbmodem1103"  # Must be changed if port changes
plotting_rate = 50 # in ms
fs = 1/(plotting_rate/1000)
list_length = int(10000 / plotting_rate)  # 10 seconds of data

#Holt EMA settings
tau_l = 0.2
tau_m = 10

#TODO: STFT settings
N = int(list_length//2.5)               # Window size: 4 seconds
L = list_length//40                     # Stride: 0.25 seconds
spec_length = (list_length - N)//L      # Width of spectrogram

# Compute stft/energy with EMA if true
clean_signal = False

# Initialize flags
jamming = False
halt = False

# Check for serial communication
try:
    ser = serial.Serial(port_name, 115200, timeout=1)
    sensor_connected = True
except serial.SerialException:
    sensor_connected = False

# Initialize arrays of data
data = [1.0E-10 for i in range(list_length)]
raw_data = [1.0E-10 for i in range(list_length)]
processed_data = [1.0E-10 for i in range(list_length)]
timestamps = np.linspace(-10, 0, list_length).tolist()

# Initialize Holt EMA processing class
holt_filter = HoltEMA(tau_l, tau_m)
start_time = time.time()

# Declare plots and axes for each figure
fig1, ax1 = plt.subplots(figsize=(8, 8))
fig2, ax2 = plt.subplots(figsize=(8, 8))
fig3, ax3 = plt.subplots(figsize=(8, 8))

calibration_frames = 50
calibration_data = []
calibration_done = False
global_high_threshold = None
global_low_threshold = None
frame_count = 0

# Update function
def update(frame):
    global frame_count, calibration_done, calibration_data
    global global_high_threshold, global_low_threshold

    if sensor_connected:
        line = ser.readline().decode().strip()
    else:
        line = True
    if line and not halt:
        try:
            # Parse raw data
            if sensor_connected:
                raw_value = float(line)
            else:
                # Simulate object sensing with fake data
                raw_value = 60 + 2 * np.sin(frame * 4 * 2 * np.pi / plotting_rate) + np.random.uniform(-0.5, 0.5)
                # raw_value = 50 + 8 * (1 if (frame % 80) < (80 // 2) else 0) + np.random.normal(0, 0.25)

            # Simulate jamming with fake data
            if jamming:
                raw_value = 5 + np.random.normal(0, 0.25)
            
            # Process the data
            timestamp = time.time() - start_time
            holt_filter.spin_once(timestamp, raw_value)
            processed_value = holt_filter.predict(timestamp)

            # Update data arrays
            raw_data.append(raw_value)
            processed_data.append(processed_value)
            raw_data.pop(0)
            processed_data.pop(0)

            # Update the distance plot
            ax1.clear()
            ax1.plot(timestamps, raw_data, label = "Raw Data")
            ax1.plot(timestamps, processed_data, label = "Processed Data")
            ax1.set_ylim(0, 300)
            ax1.set_xlim(-10, 0)
            ax1.legend(loc="upper left")
            ax1.set_xlabel("Time (seconds)")
            ax1.set_ylabel("Distance (cm)")

            window = np.ones(N)
            if clean_signal:
                input_data = processed_data
            else:
                input_data = raw_data

            X = stft(input_data, window, L)
            t = np.linspace(-10*(list_length - N)/list_length, 0, (list_length - N)//L)
            f = np.linspace(0, fs/2, N//2)

            # with open("output.txt", "a") as file:
            #         line = ' '.join(str(x) for x in X[:, spec_length-1])
            #         file.write(line + '\n')

            # with open("frequencies.txt", "a") as file:
            #         line = ' '.join(str(x) for x in frequency_powers)
            #         file.write(line + '\n')

            ax2.clear()
            ax2.pcolormesh(t, f, X, shading='gouraud', cmap='inferno', vmin=0, vmax=70)
            ax2.title.set_text("Log-Amplitude Spectrogram")
            ax2.set_xlabel("Time")
            ax2.set_ylabel("Frequency (Hz)")

            frequency_powers = np.sum(X[:, -1:], axis=1)
            mean_frequency_power = np.mean(frequency_powers)
            if mean_frequency_power > 1000/24:
                spoof_detect = True
            else:
                spoof_detect = False

            # Future improvement: Adjust thresholding for relative change instead of absolute change
            
            power_values = np.sum(X, axis=0)

            frame_count += 1
            if not calibration_done:
                calibration_data.append(np.median(power_values))
                if frame_count >= calibration_frames:
                    baseline = np.median(calibration_data)
                    std_dev = np.std(calibration_data)
                    global_high_threshold = baseline + 2*std_dev
                    global_low_threshold = baseline - 2*std_dev
                    calibration_done = True

            if calibration_done:
                high_threshold = global_high_threshold
                low_threshold = global_low_threshold
            else:
                high_threshold = 1000
                low_threshold = -100

            classification = np.zeros(len(t))
            high_indices = np.where(power_values > high_threshold)[0]
            low_indices = np.where(power_values < low_threshold)[0]
            classification[high_indices] = 1
            classification[low_indices] = 1

            min_dwell_frames = 3
            regions = []
            jamming_start = None
            end = None
            for i, elem in enumerate(classification):
                if elem == 1:
                    if jamming_start is None:
                        jamming_start = i
                else:
                    if jamming_start is not None:
                        if (i-jamming_start) >= min_dwell_frames:
                            regions.append((jamming_start, i - 1))
                        jamming_start = None
            # If the last frames are "Jamming"
            if jamming_start is not None and (len(classification) - jamming_start) >= min_dwell_frames:
                regions.append((jamming_start, len(classification) - 1))
                jam_detect = True
            else:
                jam_detect = False


            if spoof_detect:
                ax1.set_title("Spoofing Detected")
            elif jam_detect:
                ax1.set_title("Jamming Detected")
            else:
                ax1.set_title("No Attack Detected")

            ax3.clear()
            ax3.plot(t, power_values, label="Total Spectral Power", marker='o')
            ax3.axhline(y=high_threshold, color='red', linestyle='--', label="High Threshold")
            ax3.axhline(y=low_threshold, color='blue', linestyle='--', label="Low Threshold")
            ax3.set_xlim(-6, 0)
            ax3.set_xlabel("Time Frame (Index)")
            ax3.set_ylabel("Total Power (Linear Units)")
            ax3.set_title("Spectral Power Analysis for Jamming Detection")

            for (start, end) in regions:
                # Shade the region where jamming is detected
                # Extending a little to visually capture the region
                ax3.axvspan(t[start], t[end], color='red', alpha=0.2)
                start_frac = start/len(t)
                end_frac = end/len(t)
                start_distplot = int(len(timestamps)*start_frac)
                end_distplot = int(len(timestamps)*end_frac)
                ax1.axvspan(timestamps[start_distplot], timestamps[end_distplot], color='red', alpha=0.2)
        except ValueError:
            print("Error in Update Function. Check variables and types.")

# Handle keypress events
def on_key(event):
    global jamming
    global halt
    if event.key == 'q':    # Press 'q' to quit
        plt.close('all')
    elif event.key == 'j':  # Press 'j' to toggle jamming
        jamming = not jamming
    elif event.key == 'p':  # Press 'p' to pause the plotting
        halt = not halt

def stft(x, window, stride):
    time_length = (len(x) - len(window))//stride
    X = np.zeros((len(window)//2, time_length), dtype=np.float64)
    for i in range(0, time_length):
        data = x[i*stride:i*stride+len(window)]
        freq_data = np.abs(np.fft.fft(data * window, len(window)))
        freq_data[freq_data == 0] = 1e-10
        freq_data = freq_data[:len(freq_data)//2]
        X[:, i] = 20*np.log10(freq_data)
    return X

# Main loop

open("output.txt", "w").close()
open("frequencies.txt", "w").close()
fig1.canvas.mpl_connect('key_press_event', on_key)
fig2.canvas.mpl_connect('key_press_event', on_key)
fig3.canvas.mpl_connect('key_press_event', on_key)

ani1 = animation.FuncAnimation(fig1, update, interval=plotting_rate, save_count=list_length)
ani2 = animation.FuncAnimation(fig2, update, interval=plotting_rate, save_count=list_length)
ani3 = animation.FuncAnimation(fig3, update, interval=plotting_rate, save_count=list_length)

plt.show()
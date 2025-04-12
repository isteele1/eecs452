# Plotting function to run on a PC as a demonstration
# Takes in a single string of "raw_data" as a float

import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from spoofing import HoltEMA
from spoofing import JammingDetector
import time

# Settings
port_name = "/dev/tty.usbmodem1103"  # Must be changed if port changes
plotting_rate = 100 # in ms
list_length = int(10000 / plotting_rate)  # 10 seconds of data

#TODO: Holt EMA settings
tau_l = 0.1
tau_m = 0.5

#TODO: STFT settings
N = 64
L = 2
spec_length = int((list_length - N)/L)

# 400 cm/s for top speed of hand
#TODO: Jamming detection settings
drop_threshold = 10                      # drop of drop window data in cm
flatness_threshold = 1                  # range of window data in cm
window_size = int(2000 / plotting_rate)  # full window (~2000ms)
drop_window = int(500 / plotting_rate)   # how many samples ago to compare against (~500ms)

#TODO: Toggle if sensor is connected for proper debugging away from an STM/Arduino
sensor_connected = True                # Set to True if sensor is sending raw data to USB

# Initialize flags
jamming = False
spoofing = False

# Initialize arrays and serial communication
if sensor_connected:
    ser = serial.Serial(port_name, 115200, timeout=1)
data = [1.0E-6 for i in range(list_length)]
raw_data = [1.0E-6 for i in range(list_length)]
processed_data = [1.0E-6 for i in range(list_length)]
timestamps = np.linspace(-10, 0, list_length).tolist()

# Initialize processing classes
holt_filter = HoltEMA(tau_l, tau_m)
jamming_detector = JammingDetector(drop_threshold, flatness_threshold, window_size, drop_window)
start_time = time.time()

# Plot update function
def update(frame):
    if not sensor_connected:
        line = True
    else:
        line = ser.readline().decode().strip()
    if line:
        try:
            # Parse raw data
            if sensor_connected:
                raw_value = float(line)
            else:
                #TODO: Adjust the kind of data to put in if sensor is not connected
                raw_value = 60 + 2 * np.sin(frame * 4 * 2 * np.pi / plotting_rate) + np.random.uniform(-0.5, 0.5)
                # raw_value = 50 + 8 * (1 if (frame % 80) < (80 // 2) else 0) + np.random.normal(0, 0.25)
            
            if jamming:
                raw_value = 5 + np.random.normal(0, 0.25)
            raw_data.append(raw_value)

            # Process the data
            timestamp = time.time() - start_time
            holt_filter.spin_once(timestamp, raw_value)
            processed_value = holt_filter.predict(timestamp)
            processed_data.append(processed_value)

            # Check for jamming
            jam_detect, maybe_jam_detect = jamming_detector.update(raw_value)
            spoof_detect = False    # TODO

            # Update the data arrays
            raw_data.pop(0)
            processed_data.pop(0)

            # Update the plot
            ax1.clear()
            ax1.plot(timestamps, raw_data, label = "Raw Data")
            ax1.plot(timestamps, processed_data, label = "Processed Data")
            ax1.set_ylim(0, 800)
            ax1.set_xlim(-10, 0)
            ax1.legend(loc="upper left")
            ax1.set_xlabel("Time (seconds)")
            ax1.set_ylabel("Distance (cm)")

            
            if jam_detect:
                ax1.title.set_text("Attack Type: Jamming")
            elif spoof_detect:
                ax1.title.set_text("Attack Type: Spoofing")
            else:
                if maybe_jam_detect:
                    ax1.title.set_text("Possible Jamming Detected")
                else:
                    ax1.title.set_text("No Jamming Detected")
            
            fs = 1/(plotting_rate/1000)
            spectrogram_rect = np.zeros((int(N/2), spec_length))
            for i in range(0, spec_length):
                data_window = raw_data[i*L:i*L+N]
                win = np.fft.fft(data_window, N)
                temp_mag = np.abs(win[:len(win)//2])
                temp_mag[temp_mag == 0] = 1e-10
                spectrogram_rect[:, i] = 20*np.log10(temp_mag)  # Spectrogram data
            open("output.txt", "w").close()
            with open("output.txt", "a") as f:
                    line = ' '.join(str(x) for x in spectrogram_rect[:, spec_length-1])
                    f.write(line + '\n')
            time_ms = np.arange(spec_length) * (L / fs)
            freq_kHz = np.linspace(0, fs/2, int(N/2))
            ax2.clear()
            ax2.pcolormesh(time_ms, freq_kHz, spectrogram_rect, shading='gouraud', cmap='inferno', vmin=0, vmax=70)
            ax2.title.set_text("Log-Amplitude Spectrogram")
            ax2.set_xlabel("Time")
            ax2.set_ylabel("Frequency")
        except ValueError:
            print("Error: Incorrect type. Please enter a valid string of numbers with comma separation.")

# Handle keypress events
def on_key(event):
    global jamming
    global spoofing
    if event.key == 'q':    # Press 'q' to quit
        plt.close()
    elif event.key == 'j':  # Press 'j' to toggle jamming
        jamming = not jamming
    elif event.key == 's':  # Press 's' to toggle spoofing
        spoofing = not spoofing

def detect_high_freq(window, fs, threshold_freq, some_threshold):
    N = len(window)
    freq = np.fft.fftfreq(N, d=1/fs)
    spectrum = np.abs(np.fft.fft(window))

    # Normalize
    spectrum /= np.max(spectrum)

    # Detect power in high-frequency bins
    high_freq_power = np.sum(spectrum[freq > threshold_freq])
    return high_freq_power > some_threshold

# Main loop
fig, (ax1, ax2) = plt.subplots(1, 2)

fig.canvas.mpl_connect('key_press_event', on_key)
ani = animation.FuncAnimation(fig, update, interval=plotting_rate, save_count=list_length)
plt.show()
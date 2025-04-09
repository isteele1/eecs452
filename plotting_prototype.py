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
portName = "/dev/tty.usbmodem1103"  # Must be changed if port changes
plottingRate = 50 # in ms
listLength = int(10000 / plottingRate)  # 10 seconds of data

# Square wave settings
amplitude = 8
period = 80  # in frames (i.e., how many frames for one full cycle)
noise = 1

#TODO: Holt EMA settings
tau_l = 0.25
tau_m = 1

#TODO: Jamming detection settings
drop_threshold = 10                      # drop of drop window data in cm
flatness_threshold = 1                  # range of window data in cm
window_size = int(2000 / plottingRate)  # full window (~2000ms)
drop_window = int(500 / plottingRate)   # how many samples ago to compare against (~500ms)

#TODO: Toggle if sensor is connected for proper debugging away from an STM/Arduino
sensor_connected = False                # Set to True if sensor is sending raw data to USB

# Flags
jamming = False
spoofing = False

# Initialize arrays and serial communication
if sensor_connected:
    ser = serial.Serial(portName, 115200, timeout=1)
data = [0.0 for i in range(listLength)]
raw_data = [0.0 for i in range(listLength)]
processed_data = [0.0 for i in range(listLength)]
timestamps = np.linspace(-10, 0, listLength).tolist()

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
                raw_value = 60 + 2 * np.sin(frame * 0.1) + np.random.uniform(-0.5, 0.5)
                # raw_value = 50 + amplitude * (1 if (frame % period) < (period // 2) else 0) + np.random.normal(0, 0.25)
            
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
            ax.clear()
            ax.plot(timestamps, raw_data, label = "Raw Data")
            ax.plot(timestamps, processed_data, label = "Processed Data")
            ax.set_ylim(0, 100)
            ax.set_xlim(-10, 0)
            if jam_detect:
                ax.title.set_text("Attack Type: Jamming")
            elif spoof_detect:
                ax.title.set_text("Attack Type: Spoofing")
            else:
                if maybe_jam_detect:
                    ax.title.set_text("Possible Jamming Detected")
                else:
                    ax.title.set_text("No Jamming Detected")
            
            ax.legend(loc="upper left")
            ax.set_xlabel("Time (seconds)")
            ax.set_ylabel("Distance (cm)")
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

# Main loop
fig, ax = plt.subplots()
fig.canvas.mpl_connect('key_press_event', on_key)
ani = animation.FuncAnimation(fig, update, interval=plottingRate)
plt.show()
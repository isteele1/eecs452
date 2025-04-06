import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Settings
portName = "/dev/tty.usbmodem1103"  # Must be changed if port changes
plottingRate = 250 # in ms
listLength = int(10000 / plottingRate)  # 10 seconds of data

# Initializing
ser = serial.Serial(portName, 115200, timeout=1)
data = [0.0 for i in range(listLength)]
naive_data = [0.0 for i in range(listLength)]
processed_data = [0.0 for i in range(listLength)]
timestamps = np.linspace(-10, 0, listLength).tolist()

# Plot update function
def update(frame):
    line = ser.readline().decode().strip()
    if line:
        try:
            # Parse the string into a list
            list = str.split(line, ",")

            # Update the data
            naive_data.append(float(list[0]))
            processed_data.append(float(list[1]))
            naive_data.pop(0)
            processed_data.pop(0)

            # Update the plot
            ax.clear()
            ax.plot(timestamps, naive_data, label = "Naive Sensing")
            ax.plot(timestamps, processed_data, label = "Processed Output")
            ax.set_ylim(0, 256)
            ax.set_xlim(-10, 0)
            ax.legend(loc="upper left")
            ax.set_xlabel("Time (seconds)")
            ax.set_ylabel("Distance (cm)")
        except ValueError:
            print("Error: Incorrect type. Please enter a valid string of numbers with comma separation.")

# Handle keypress events
def on_key(event):
    global running
    if event.key == 'q':  # Press 'q' to quit
        running = False
        plt.close()  # Close the plot window

# Main loop
fig, ax = plt.subplots()
fig.canvas.mpl_connect('key_press_event', on_key)
ani = animation.FuncAnimation(fig, update, interval=plottingRate)
plt.show()
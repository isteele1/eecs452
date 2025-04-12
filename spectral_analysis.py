import numpy as np
import matplotlib.pyplot as plt
import sys

def load_spectral_data(file_name):
    spectral_data = []
    with open(file_name, 'r') as f:
        for line in f:
            if line.strip():
                row = np.array([float(x) for x in line.strip().split()])
                spectral_data.append(row)
    if not spectral_data:
        return np.array([])
    return np.vstack(spectral_data)
#takes output.txt data and turns it into 2D numpy array to separate spectral data into different time periods

def compute_total_power(spectrum_dB):
    linear_power = 10 ** (spectrum_dB / 10)
    total_power = np.sum(linear_power)
    return total_power
#convert spectrum values into linear power and then sum for total power

def analyze_spectral_data(spectral_data, threshold):
    num_frames = spectral_data.shape[0]
    power_values = np.zeros(num_frames)
    classification = []

    for i in range(num_frames):
        total_power = compute_total_power(spectral_data[i])
        power_values[i] = total_power
        if total_power > threshold:
            classification.append("Jamming")
        else:
            classification.append("No Jamming")
    return power_values, classification
#compute linear scale of spectral power for each time period, use thresholds to decide jam or no jam


def main():
    file_name = "output.txt"
    if len(sys.argv) > 2:
        threshold = float(sys.argv[2])
    else:
        threshold = 1e3

    spectral_data = load_spectral_data(file_name)
    power_values, classification = analyze_spectral_data(spectral_data, threshold)

    for i, (power, cls) in enumerate(zip(power_values, classification)):
        print(f"Frame {i}: Total Power = {power:.2f} -> {cls}")

    # Plot the spectral power over time with the threshold line (from chat)
    plt.figure(figsize=(10, 4))
    plt.plot(power_values, label="Total Spectral Power", marker='o')
    plt.axhline(y=threshold, color='red', linestyle='--', label="Threshold")
    plt.xlabel("Time Frame (Index)")
    plt.ylabel("Total Power (Linear Units)")
    plt.title("Spectral Power Analysis for Jamming Detection")
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Optionally, plot a histogram to see the distribution of total power values (from chat)
    plt.figure(figsize=(8, 4))
    plt.hist(power_values, bins=20, color='skyblue', edgecolor='k')
    plt.axvline(x=threshold, color='red', linestyle='--', label="Threshold")
    plt.xlabel("Total Power (Linear Units)")
    plt.ylabel("Count")
    plt.title("Histogram of Total Spectral Power")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
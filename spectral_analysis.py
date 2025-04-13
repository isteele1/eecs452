import numpy as np
import matplotlib.pyplot as plt
import sys

def load_spectral_data(file_name):
    spectral_data = []
    with open(file_name, 'r') as f:
        for line in f:
            if line.strip():
                # Convert the line into a numpy array of floats
                row = np.array([float(x) for x in line.strip().split()])
                spectral_data.append(row)
    if not spectral_data:
        return np.array([])
    return np.vstack(spectral_data)


def compute_total_power(spectrum_dB):
    # Convert dB values to linear power
    linear_power = 10 ** (spectrum_dB / 10)
    total_power = np.sum(linear_power)
    return total_power


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

def get_jamming_regions(classification):
    regions = []
    start = None
    for i, label in enumerate(classification):
        if label == "Jamming":
            if start is None:
                start = i
        else:
            if start is not None:
                regions.append((start, i - 1))
                start = None
    # If the last frames are "Jamming"
    if start is not None:
        regions.append((start, len(classification) - 1))
    return regions


def main():
    # Parse command line arguments for file name and threshold value
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = "output.txt"

    # Default threshold in linear power units (change this value if needed)
    if len(sys.argv) > 2:
        threshold = float(sys.argv[2])
    else:
        threshold = 0.2*1e9  # example default value; adjust as needed

    print(f"Loading spectral data from {file_name}...")
    spectral_data = load_spectral_data(file_name)
    if spectral_data.size == 0:
        print("No spectral data found in file.")
        return

    print("Performing power spectral analysis...")
    power_values, classification = analyze_spectral_data(spectral_data, threshold)

    # Output the classification for each frame
    for i, (power, cls) in enumerate(zip(power_values, classification)):
        print(f"Frame {i}: Total Power = {power:.2f} -> {cls}")

    # Plot the spectral power over time with the threshold line and highlight jamming areas
    fig, ax = plt.subplots(figsize=(10, 4))
    x = np.arange(len(power_values))
    ax.plot(x, power_values, label="Total Spectral Power", marker='o')
    ax.axhline(y=threshold, color='red', linestyle='--', label="Threshold")
    ax.set_xlabel("Time Frame (Index)")
    ax.set_ylabel("Total Power (Linear Units)")
    ax.set_title("Spectral Power Analysis for Jamming Detection")

    # Identify regions where jamming is detected
    jamming_regions = get_jamming_regions(classification)
    for (start, end) in jamming_regions:
        # Shade the region where jamming is detected
        # Extending a little to visually capture the region
        ax.axvspan(start - 0.5, end + 0.5, color='red', alpha=0.2)

    ax.legend()
    plt.tight_layout()
    plt.show()

    # Optionally, plot a histogram to see the distribution of total power values
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

file_path = "frequencies_spoofing_slow.txt"  # change this if your file has a different name

all_values = []

with open(file_path, 'r') as f:
    for line in f:
        # Split line into float numbers, ignoring empty lines
        if line.strip():
            values = map(float, line.strip().split())
            all_values.extend(values)

# Calculate min and max
if all_values:
    min_val = min(all_values)
    max_val = max(all_values)
    mean_val = sum(all_values) / len(all_values)
    standard_deviation = (sum((x - mean_val) ** 2 for x in all_values) / len(all_values)) ** 0.5
    print(f"Minimum value: {min_val}")
    print(f"Maximum value: {max_val}")
    print(f"Mean value: {mean_val}")
    print(f"Standard deviation: {standard_deviation}")
else:
    print("The file contains no float values.")
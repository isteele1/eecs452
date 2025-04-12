file_path = "output.txt"  # change this if your file has a different name

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
    print(f"Minimum value: {min_val}")
    print(f"Maximum value: {max_val}")
else:
    print("The file contains no float values.")
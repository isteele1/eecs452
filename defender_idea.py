import time

def detect_attack(pulses, window_size=10):
    """
    Check the last window_size pulses to see if they match the attacker pattern:
    - All pulses have the same lower limit (0)
    - All pulses have the same upper limit (1)
    - All pulses report the same trig pin (e.g., 9)
    """
    if len(pulses) < window_size:
        return False  # Not enough data to decide
    
    # Use the most recent window of pulses
    window = pulses[-window_size:]
    lower_vals = [p[0] for p in window]
    upper_vals = [p[1] for p in window]
    trig_vals  = [p[2] for p in window]
    
    # Check if all values in the window are constant and match the attacker pattern
    if (all(val == lower_vals[0] for val in lower_vals) and 
        all(val == upper_vals[0] for val in upper_vals) and 
        all(val == trig_vals[0] for val in trig_vals)):
        
        if lower_vals[0] == 0 and upper_vals[0] == 1:
            return True

    return False

def main():
    """
    In a real deployment, pulses would be read from the sensor or serial input.
    Here we simulate pulse readings. Under normal operation, pulse values might vary,
    but an attack injects constant values: (0, 1, 9).
    """
    pulses = []
    
    while True:
        # --- Simulation of sensor data reading ---
        # Replace this with code that reads actual sensor data.
        # For an attacker, each pulse would be (0, 1, 9)
        new_pulse = (0, 1, 9)
        pulses.append(new_pulse)
        
        # Check for the attacker pattern in the latest pulses
        if detect_attack(pulses):
            print("Attack detected!")
        else:
            print("Normal sensor operation")
        
        # Delay to simulate sensor pulse interval (e.g., 50 ms)
        time.sleep(0.05)

if __name__ == "__main__":
    main()

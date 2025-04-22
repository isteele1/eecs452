import numpy as np
import time

def detect_sine_attack(delays, period=200, correlation_threshold=0.9):
    """
    Examine the most recent 'period' delay values to see if they follow a sine-wave pattern.
    
    The expected pattern is:
      delayTime = 2 + (998 * (sin(2*pi*t/period) + 1) / 2)
      
    We allow for an unknown phase shift by rolling the expected array.
    
    Parameters:
      delays (list or array): Recent delay time measurements.
      period (int): Number of samples corresponding to one full sine cycle.
      correlation_threshold (float): Minimum correlation to flag an attack.
      
    Returns:
      bool: True if an attack is detected, False otherwise.
    """
    if len(delays) < period:
        return False  # Not enough data to decide
    
    # Consider only the most recent 'period' samples
    recent_delays = np.array(delays[-period:])
    # Create expected sine pattern for one period (values in microseconds)
    t = np.arange(period)
    expected = 2 + (998 * (np.sin(2 * np.pi * t / period) + 1) / 2)
    
    max_corr = 0
    # Try all possible phase shifts by rolling the expected array
    for shift in range(period):
        expected_shifted = np.roll(expected, shift)
        corr_matrix = np.corrcoef(recent_delays, expected_shifted)
        corr = corr_matrix[0, 1]
        if corr > max_corr:
            max_corr = corr
    
    # Debug: Print maximum correlation for insight
    # print(f"Max correlation: {max_corr:.3f}")
    
    return max_corr > correlation_threshold

def main():
    """
    In a real deployment, delay times would be measured from sensor trigger intervals.
    Here we simulate readings that mimic the attacker’s sine-wave delay.
    
    Under attack, each measured delay is computed as:
      delayTime = 2 + (998 * (sin(2*pi*timeStep/period) + 1) / 2)
    """
    delays = []      # List to store measured delay times (in microseconds)
    timeStep = 0     # Simulated time step index (0 to period-1)
    period = 200     # Cycle period as defined in the attacker code
    
    while True:
        # Simulate the attacker's delayTime calculation
        normalizedTime = timeStep / period
        delayTime = 2 + (998 * (np.sin(2 * np.pi * normalizedTime) + 1) / 2)
        
        # In a live system, this value would be measured from sensor readings
        delays.append(delayTime)
        
        # Check if the most recent set of delays matches the sine attack pattern
        if detect_sine_attack(delays, period=period):
            print("Attack detected! Sine wave pattern in delay times.")
        else:
            print("Normal sensor operation.")
        
        # Increment timeStep and wrap around after a full period
        timeStep = (timeStep + 1) % period
        
        # Sleep to simulate the cycle; note: actual Arduino delays are in microseconds,
        # but here we use a longer sleep to make the simulation observable.
        time.sleep(0.01)

if __name__ == "__main__":
    main()

# Holds classes used in plotting_prototype.py
import numpy as np

#EMA for tracking timestamps
class HoltEMA:
    #Predict a trendline of the form y=mx+b given samples of x and b
    def __init__(self, tau_l, tau_m):
        self.tau_l = float(tau_l)
        self.tau_m = float(tau_m)
        self.m = 0.0
        self.l = 0.0
        self.x = 0.0

    def spin_once(self, x, y):
        x = float(x)
        y = float(y)
        x_prev = self.x
        l_prev = self.l
        m_prev = self.m

        # Input sample difference
        delta_x = x - x_prev
        
        if delta_x > 0:

            a_l = 1 - np.exp(-1*delta_x / self.tau_l)
            a_m = 1 - np.exp(-1*delta_x / self.tau_m)

            #Update l and m
            y_k_star = m_prev * delta_x + l_prev
            self.l = a_l * y + (1 - a_l) * y_k_star
            self.m = a_m * (self.l - l_prev) / delta_x + (1 - a_m) * m_prev

            self.x = x
    
    def predict(self, x):
        return (self.m*(x - self.x) + self.l)
    
    def predict_optimal_send(self, y):
        return round((y - self.l)/self.m) + self.x
    
class JammingDetector:
    def __init__(self, drop_threshold=20.0, flatness_threshold=0.5, window_size=20, drop_window=5):
        self.drop_threshold = drop_threshold
        self.flatness_threshold = flatness_threshold
        self.window_size = window_size
        self.drop_window = drop_window
        self.recent_values = []
        self.maybe_jamming = False
        self.jamming = False

    def update(self, new_value):

        # Update recent values
        self.recent_values.append(new_value)
        if len(self.recent_values) > self.window_size:
            self.recent_values.pop(0)

        # Sudden drop detection over a short window
        if len(self.recent_values) >= self.drop_window + 1:
            previous_max = max(self.recent_values[:self.drop_window])
            drop = previous_max - new_value
            if drop > self.drop_threshold:
                self.maybe_jamming = True

        # Flatness check for confirmation
        if self.maybe_jamming and len(self.recent_values) >= self.window_size:
            # variance = np.var(self.recent_values[:round(len(self.recent_values)/2)])
            variance = np.max(self.recent_values) - np.min(self.recent_values)
            if variance < self.flatness_threshold:
                self.jamming = True
            else:
                self.jamming = False
                self.maybe_jamming = False  # Reset if not flat

        return self.jamming, self.maybe_jamming
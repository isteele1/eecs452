#include "HoltEMA.h"
#include "kiss_fft.h"

#include <vector>
#include <iostream>
#include <cmath>
#include <chrono>
#include <random>

using namespace std;
using namespace std::chrono;

HoltEMA::HoltEMA(double tau_l_, double tau_m_) : tau_l(tau_l_), tau_m(tau_m_) {}

vector<double> hamming(int N) {
    vector<double> window(N);

    for (int n = 0; n < N; ++n) {
        window[n] = 0.54 - 0.46 * cos((2 * M_PI * n) / (N - 1));
    }

    return window;
}   // End hamming()

vector<vector<double>> stft(const kiss_fft_cfg &cfg, const deque<double> &x, const vector<double> &window, int stride) {
    int window_size = window.size();
    if (window_size < x.size()) {
        throw invalid_argument("Window size must be less than or equal to the size of the signal.");

    }
    int time_length = (x.size() - window_size) / stride;
    int freq_bins = window_size / 2;

    vector<vector<double>> X(freq_bins, vector<double>(time_length, 0.0));

    vector<kiss_fft_cpx> in(window_size);
    vector<kiss_fft_cpx> out(window_size);

    for (int i = 0; i < time_length; ++i) {
        int start = i * stride;

        // Prepare input with window applied
        for (int j = 0; j < window_size; ++j) {
            in[j].r = x[start + j] * window[j];
            in[j].i = 0.0;
        }

        // Run FFT
        kiss_fft(cfg, in.data(), out.data());

        // Compute magnitude spectrum (log-scaled)
        for (int k = 0; k < freq_bins; ++k) {
            double real = out[k].r;
            double imag = out[k].i;
            double magnitude = std::sqrt(real * real + imag * imag);
            if (magnitude == 0.0) magnitude = 1e-10;
            X[k][i] = 20 * std::log10(magnitude);
        }
    }

    return X;
}   // End stft()

int main () {

    // Plotting rate
    double plotting_rate = 5;   // in ms
    double fs = 1/(plotting_rate/1000);     // sampling frequency
    int list_length = int(10000 / plotting_rate);   // 10 seconds of data

    // STFT settings
    int N = 50;             // Window size: 4 seconds
    int L = 50;             // Stride: 0.25 seconds

    // Holt EMA settings
    double tau_l = 0.2;
    double tau_m = 10;

    double initial_value = 1.0E-10;

    deque<double> raw_data(list_length, initial_value);
    deque<double> processed_data(list_length, initial_value);

    HoltEMA holt_filter = HoltEMA(tau_l, tau_m);
    auto start_time = high_resolution_clock::now();

    // Create window
    // vector<double> window(N, 1); // Rectangular window could be used if needed
    vector<double> hamm = hamming(N);

    kiss_fft_cfg cfg = kiss_fft_alloc(N, 0, nullptr, nullptr);
    while (true) {
        // Placeholder data incoming
        double raw_val = 40.5;
        // Clock math
        auto end_time = high_resolution_clock::now();
        duration<double> elapsed = end_time - start_time;
        double time_secs = elapsed.count();

        // Spin Holt EMA for processing
        holt_filter.spin_once(time_secs, raw_val);
        double processed_val = holt_filter.predict(time_secs);

        // Update data arrays
        raw_data.push_back(raw_val);
        processed_data.push_back(processed_val);
        raw_data.pop_front();
        processed_data.pop_front();

        // STFT Processing
        vector<vector<double>> X = stft(cfg, raw_data, hamm, L);

        // Output distance data points
        cout << raw_val << " " << processed_val << "\n";

        // Output most recent STFT column
        for (size_t i = 0; i < X.back().size() - 1; i++) {
            cout << X.back()[i] << " ";
        }
        cout << X.back().back() << "\n";
    }
    free(cfg);
}   // End main()

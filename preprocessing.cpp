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

vector<vector<double>> stft(const deque<double>& x, const vector<double>& window, int stride) {
    int window_size = window.size();
    int time_length = (x.size() - window_size) / stride;
    int freq_bins = window_size / 2;

    vector<vector<double>> X(freq_bins, vector<double>(time_length, 0.0));

    kiss_fft_cfg cfg = kiss_fft_alloc(window_size, 0, nullptr, nullptr);
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

    free(cfg);
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
    double spec_length = (list_length - N)/L;      // Width of spectrogram

    // Holt EMA settings
    double tau_l = 0.2;
    double tau_m = 10;

    cout << "Sampling Frequency: " << fs << endl;
    cout << "Data Length: " << list_length << endl;
    cout << "Dimensions of STFT: " << N/2 << "x" << spec_length << endl;

    double initial_value = 1.0E-10;

    deque<double> raw_data(list_length, initial_value);
    deque<double> processed_data(list_length, initial_value);

    HoltEMA holt_filter = HoltEMA(tau_l, tau_m);
    auto start_time = high_resolution_clock::now();

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

        // STFT processing
        vector<double> window(N, 1);
        vector<vector<double>> X = stft(raw_data, window, L);

        // Output distance data points
        cout << raw_val << " " << processed_val << "\n";

        // Output most recent STFT column
        for (size_t i = 0; i < X.back().size() - 1; i++) {
            cout << X.back()[i] << " ";
        }
        cout << X.back().back() << "\n";
    }
}   // End main()

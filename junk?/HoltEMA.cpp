// HoltEMA.cpp
#include "HoltEMA.h"
#include <cmath>

HoltEMA::HoltEMA(double tau_l_, double tau_m_)
    : tau_l(tau_l_), tau_m(tau_m_), m(0.0), l(0.0), x(0.0) {}

void HoltEMA::spin_once(double x_new, double y) {
    double delta_x = x_new - x;

    if (delta_x > 0.0) {
        double a_l = 1.0 - std::exp(-delta_x / tau_l);
        double a_m = 1.0 - std::exp(-delta_x / tau_m);

        double y_k_star = m * delta_x + l;
        double l_new = a_l * y + (1.0 - a_l) * y_k_star;
        double m_new = a_m * (l_new - l) / delta_x + (1.0 - a_m) * m;

        l = l_new;
        m = m_new;
        x = x_new;
    }
}

double HoltEMA::predict(double x_new) const {
    return m * (x_new - x) + l;
}
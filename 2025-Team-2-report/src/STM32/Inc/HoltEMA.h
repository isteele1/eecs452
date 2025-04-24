// HoltEMA.h
#ifndef HOLTEMA_H
#define HOLTEMA_H

class HoltEMA {
private:
    double tau_l;
    double tau_m;
    double m;
    double l;
    double x;

public:
    HoltEMA(double tau_l_, double tau_m_);
    void spin_once(double x_new, double y);
    double predict(double x_new) const;
};

#endif
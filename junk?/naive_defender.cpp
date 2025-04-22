#include <iostream>
#include <chrono>
#include <thread>
#include "stm32f1xx_hal.h"   // or your series
#include <cstdio>            // for sprintf
#include <cstring>           // for strlen

using std::cout;
using std::endl;
using std::this_thread::sleep_for;
using std::chrono::high_resolution_clock;
using std::chrono::microseconds;
using std::chrono::milliseconds;
using std::chrono::duration_cast;

extern UART_HandleTypeDef huart2;  // UART handle defined by STM32CubeMX

void sendDistance(float naive_distance, float cleaned_distance) {
    char buffer[64];
    sprintf(buffer, "%.2f,%.2f\r\n", naive_distance, cleaned_distance);  // Format as CSV
    HAL_UART_Transmit(&huart2, (uint8_t*)buffer, strlen(buffer), HAL_MAX_DELAY);
}

// ---- GPIO placeholders (replace with real functions for your platform) ----
void digitalWrite(int pin, bool value) {
    // TODO: Add actual GPIO control
}
bool digitalRead(int pin) {
    // TODO: Add actual GPIO read
    return false;
}
void pinMode(int pin, bool is_output) {
    // TODO: Set pin direction
}

// ---- Timing helpers ----
void delayMicroseconds(int us) {
    sleep_for(microseconds(us));
}

// Simulate Arduino-style pulseIn (duration in microseconds)
long pulseIn(int pin, bool state) {     // assumed state is HIGH or true
    auto start_time = high_resolution_clock::now();

    // Wait for pin to reach desired state
    while (digitalRead(pin) != state);

    auto pulse_start = high_resolution_clock::now();

    // Measure how long the pin stays in that state
    while (digitalRead(pin) == state);

    auto pulse_end = high_resolution_clock::now();
    return duration_cast<microseconds>(pulse_end - pulse_start).count();
}

// ---- Ultrasonic Distance Calculation ----
float getDistance(int trigPin, int echoPin) {
    digitalWrite(trigPin, false);
    delayMicroseconds(2);

    digitalWrite(trigPin, true);
    delayMicroseconds(10);
    digitalWrite(trigPin, false);

    long duration = pulseIn(echoPin, true);
    return duration * 0.034f / 2;
}

// ---- Main Loop ----
int main() {
    const int trigPin = 9;
    const int echoPin = 10;

    int sensing_delay = 500;

    pinMode(trigPin, true);   // OUTPUT
    pinMode(echoPin, false);  // INPUT

    while (true) {
        float distance = getDistance(trigPin, echoPin);
        sendDistance(distance, distance);
        sleep_for(milliseconds(sensing_delay));
    }

    return 0;
}
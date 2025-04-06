#include <iostream>
#include <chrono>
#include <thread>

using std::cout;
using std::endl;
using std::this_thread::sleep_for;
using std::chrono::high_resolution_clock;
using std::chrono::microseconds;
using std::chrono::milliseconds;
using std::chrono::duration_cast;
// Selectively import needed std components
using std::cout;
using std::endl;
using std::this_thread::sleep_for;
using std::chrono::high_resolution_clock;
using std::chrono::microseconds;
using std::chrono::milliseconds;
using std::chrono::duration_cast;

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

    pinMode(trigPin, true);   // OUTPUT
    pinMode(echoPin, false);  // INPUT

    while (true) {
        float distance = getDistance(trigPin, echoPin);
        cout << "Distance: " << distance << " cm" << endl;
        sleep_for(milliseconds(500));
    }

    return 0;
}
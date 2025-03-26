// Define the pins for the HC-SR04 sensor
const int trigPin = 9;
const int echoPin = 10;

const int period = 200; // Total cycle time in milliseconds
const float pi = 3.14159;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  static int timeStep = 0;
  float normalizedTime = (float)timeStep / period; // Normalize to range [0,1]
  int delayTime = 2 + (998 * (sin(2 * pi * normalizedTime) + 1) / 2); // Map sine wave to [2, 1000]us

  // Send 10-microsecond trigger pulse
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Wait before next pulse
  delayMicroseconds(delayTime);

  // Increment timeStep and wrap around
  timeStep = (timeStep + 1) % period;
}
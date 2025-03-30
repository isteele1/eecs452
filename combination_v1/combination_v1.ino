// Define the pins for the HC-SR04 sensor
const int trig_defend = 9;
const int echo_defend = 10;

const int trig_attack = 6
const int echo_attack = 5

int count = 200;
int zero = 0;

void setup() {
  Serial.begin(9600);

  pinMode(trig_attack, OUTPUT);
  pinMode(echo_attack, INPUT);

  pinMode(trig_defend, OUTPUT);
  pinMode(echo_defend, INPUT);

  
}

void loop() {

  // Attacker Component
  digitalWrite(trigPin, LOW);
  delay(43);
  digitalWrite(trigPin, HIGH);
  delay(78);
  digitalWrite(trigPin, LOW);
  
  
  // Defender Component
  digitalWrite(trig_defend, LOW);
  delayMicroseconds(2);
  
  // Set the trig_defend HIGH for 10 microseconds to send the pulse
  digitalWrite(trig_defend, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig_defend, LOW);
  
  // Read the echo_defend, which returns the sound wave travel time in microseconds
  long duration = pulseIn(echo_defend, HIGH);
  
  // Calculate the distance in centimeters
  // Speed of sound wave divided by 2 (to and fro)
  float distance = duration * 0.034 / 2;
  
  // Print the distance to the Serial Monitor
  Serial.print(0); // To freeze the lower limit
  Serial.print(" ");
  Serial.print(300); // To freeze the upper limit
  Serial.print(" ");
  Serial.println(distance); // To send all three 'data' points to the plotter
  
  // Wait for a short period before the next measurement
  delay(50);
  count--;

}
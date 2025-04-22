// Define the pins for the HC-SR04 sensor
const int trigPin = 9;
const int echoPin = 10;

int count = 200;
int zero = 0;
void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Set the trigPin as an OUTPUT
  pinMode(trigPin, OUTPUT);
  
  // Set the echoPin as an INPUT
  pinMode(echoPin, INPUT);
}

void loop() {
  // Clear the trigPin
  // while (count > 0){
      digitalWrite(trigPin, LOW);
      delayMicroseconds(2);
      
      // Set the trigPin HIGH for 10 microseconds to send the pulse
      digitalWrite(trigPin, HIGH);
      delayMicroseconds(10);
      digitalWrite(trigPin, LOW);
      
      // Read the echoPin, which returns the sound wave travel time in microseconds
      long duration = pulseIn(echoPin, HIGH);
      
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
  // } 

}
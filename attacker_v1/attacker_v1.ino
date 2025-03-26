// Define the pins for the HC-SR04 sensor
const int trigPin = 9;
const int echoPin = 10;

int pulseDelay = 50; // ms
int count = floor(60/(pulseDelay/1000));  // 60sec of operation

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Set the trigPin as an OUTPUT
  pinMode(trigPin, OUTPUT);
  
  // Set the echoPin as an INPUT
  pinMode(echoPin, INPUT);
}

void loop() {
  // while (count > 0){
      // Sends a pulse of HIGH for 10 microseconds on trigPin
      digitalWrite(trigPin, LOW);
      delay(43);
      digitalWrite(trigPin, HIGH);
      delay(78);
      digitalWrite(trigPin, LOW);
      Serial.print(0); // To freeze the lower limit
      Serial.print(" ");
      Serial.print(1); // To freeze the upper limit
      Serial.print(" ");
      Serial.println(trigPin); // To send all three 'data' points to the plotter

      count--;
  // }
}
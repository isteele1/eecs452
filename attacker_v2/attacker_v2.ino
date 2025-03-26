// Define the pins for the HC-SR04 sensor
const int trigPin = 9;
const int echoPin = 10;

int pulseDelay = 5; // ms
int count = floor(60/(pulseDelay/1000));  // 60sec of operation

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  Serial.println("Hello");
  // randomSeed(analogRead(0));
  
  // Set the trigPin as an OUTPUT
  pinMode(trigPin, OUTPUT);
  
  // Set the echoPin as an INPUT
  pinMode(echoPin, INPUT);
  Serial.println(count);
}

void loop() {
  while (count > 0){
      // Sends a pulse of HIGH for 10 microseconds on trigPin
      digitalWrite(trigPin, LOW);
      int rand1 = random(50, 10000);
      delayMicroseconds(rand1);
      digitalWrite(trigPin, HIGH);
      int rand2 = random(50, 10000);
      delayMicroseconds(rand2);
      digitalWrite(trigPin, LOW);

      Serial.print(0); // To freeze the lower limit
      Serial.print(" ");
      Serial.print(10000); // To freeze the upper limit
      Serial.print(" ");
      Serial.print(rand1);
      Serial.print(" ");
      Serial.println(rand2);
      count--;
  }
}
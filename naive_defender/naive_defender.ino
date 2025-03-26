const int trigPin = 9;
const int echoPin = 10;

void setup() {
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  delay(200);
  long timetofly;
  int distance;

  // Trigger the sensor
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read echo
  timetofly = pulseIn(echoPin, HIGH, 30000);  

  if (timetofly > 0) {
    distance = timetofly * 0.034 / 2;
    // Serial.print("Distance: ");
    Serial.println(distance);
  } else {
    Serial.println("No valid echo received.");
  }
  
  // No delay, run as fast as pulseIn() allows
}
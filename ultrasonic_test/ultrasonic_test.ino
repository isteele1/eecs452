void setup() {
  pinMode(9, OUTPUT);
}

void loop() {
  digitalWrite(9, LOW);
  delayMicroseconds(2);
  digitalWrite(9, HIGH);
  delayMicroseconds(10);
  digitalWrite(9, LOW);

  delay(1);
}

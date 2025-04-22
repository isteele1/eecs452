// Pin definitions
const int trig_defend = 9;
const int echo_defend = 10;
const int trig_attack = 6;

// Jamming signal parameters
volatile bool jamming_active = true; // Set to false to disable jamming
volatile uint8_t jam_pulse_phase = 0;
const uint16_t JAM_PULSE_INTERVAL = 200; // 300µs between pulses (3.33kHz)
const uint8_t JAM_PULSE_WIDTH = 5;      // 5µs pulse width

void setup() {
  Serial.begin(115200);
  
  // Initialize pins
  pinMode(trig_attack, OUTPUT);
  digitalWrite(trig_attack, LOW);
  
  pinMode(trig_defend, OUTPUT);
  pinMode(echo_defend, INPUT);
  digitalWrite(trig_defend, LOW);

  // Configure Timer1 for jamming signal
  noInterrupts();
  TCCR1A = 0;
  TCCR1B = 0;
  TCNT1 = 0;
  OCR1A = 159; // 16MHz/(1*100kHz) - 1 = 159 (10µs interrupts)
  TCCR1B |= (1 << WGM12); // CTC mode
  TCCR1B |= (1 << CS10);  // No prescaler
  TIMSK1 |= (1 << OCIE1A); // Enable timer compare interrupt
  interrupts();
}

ISR(TIMER1_COMPA_vect) { // Runs every 10µs
  static uint16_t jam_counter = 0;
  
  if(!jamming_active) {
    digitalWrite(trig_attack, LOW);
    return;
  }

  jam_counter += 10; // Increment by 10µs
  
  if(jam_pulse_phase == 0) {
    // Time to start new pulse
    if(jam_counter >= JAM_PULSE_INTERVAL) {
      digitalWrite(trig_attack, HIGH);
      jam_pulse_phase = 1;
      jam_counter = 0;
    }
  } 
  else {
    // Time to end pulse
    if(jam_counter >= JAM_PULSE_WIDTH) {
      digitalWrite(trig_attack, LOW);
      jam_pulse_phase = 0;
    }
  }
}

void loop() {
  // Normal defender operation
  digitalWrite(trig_defend, LOW);
  delayMicroseconds(2);
  digitalWrite(trig_defend, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig_defend, LOW);
  
  long duration = pulseIn(echo_defend, HIGH, 30000); // 30ms timeout
  float distance = duration * 0.034 / 2;
  
  Serial.print(0);
  Serial.print(" ");
  Serial.print(400);
  Serial.print(" ");
  Serial.println(distance);
  
  delay(100);
}

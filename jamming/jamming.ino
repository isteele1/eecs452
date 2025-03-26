
const int DAC_CHANNEL = 1; // TODO: SET DAC CHANNEL
const int PWM_CHANNEL = 0; // TODO: SET PWM CHANNEL
const int DAC_PIN = 26; // TODO: SET pin corresponding to DAC channel

volatile uint8_t sinCount = 0; // volitile count variable for sine interations

void setup() {
  Serial.begin(115200);
  // TODO: use pinMode to set your PWN pin to an output
  pinMode(PWM_CHANNEL, OUTPUT);
  // TODO: setup pwm on a channel with the desired frequency
  setupPwm(PWM_CHANNEL, 10000);
  // TODO: attach the pwm to your PWN pin
  pwmAttachPin(PWM_CHANNEL, DAC_PIN);
  // TODO: setup and start timer at desired frequency
  setUpTimer(0, timerCallback, 39.0625);
  startTimer(0);
  // R = 10.6 kOhms

}
void timerCallback(){
  // TODO: sine value calculation based on sinCount (same as Task 2.1)
  uint8_t sinVal2 = 127.5 + 127.5*sin(sinCount*2*PI/256);
  // TODO: update pwm duty cycle based on the sine value
  setPwmDuty(PWM_CHANNEL, sinVal2);
  sinCount++;   // increment sinCount whenever this callback function is called
}

void setupPwm(uint8_t chan, double freq)
{
    if(freq < 1 || 312500 < freq || chan > 15)  return;
    ledcSetup(chan, (double) freq, 8);
}

void setPwmDuty(uint8_t chan, uint16_t duty)
{
    if(chan > 15)  return;
    ledcWrite(chan, duty);
}

void pwmAttachPin(uint8_t chan, uint8_t pin)
{
    if(pin > 39)  return;
    ledcAttachPin(pin, chan);
}

void startTimer(uint8_t timer_index)
{
  switch(timer_index){
      case 0:
        timerAlarmEnable(timer_0);
        break;
      case 1:
        timerAlarmEnable(timer_1);
        break;
      case 2:
        timerAlarmEnable(timer_2);
        break;
      case 3:
        timerAlarmEnable(timer_3);
        break;
      default:
        break;
    }
}

void stopTimer(uint8_t timer_index) {
    switch(timer_index){
      case 0:
        timerEnd(timer_0);
        break;
      case 1:
        timerEnd(timer_1);
        break;
      case 2:
        timerEnd(timer_2);
        break;
      case 3:
        timerEnd(timer_3);
        break;
      default:
        break;
    }
}

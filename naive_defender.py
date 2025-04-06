import RPi.GPIO as GPIO
import time

TRIG = 9
ECHO = 10

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    # Send a 10us pulse to trigger
    GPIO.output(TRIG, False)
    time.sleep(0.000002)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for echo to start
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()

    # Wait for echo to end
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 34300 / 2  # cm

    return distance

try:
    while True:
        dist = get_distance()
        print(f"Distance: {dist:.2f} cm")
        time.sleep(0.5)

except KeyboardInterrupt:
    GPIO.cleanup()
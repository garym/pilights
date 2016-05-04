#/usr/bin/env python3

from RPi import GPIO
import time

def detector_event(channel):
    value = GPIO.input(channel)
    print('This is an edge event callback.')
    print('  Edge detected on {}.'.format(channel))
    print('  This is a {} edge.'.format('rising' if value else 'falling'))

def setup(channel, callback):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(channel, GPIO.BOTH, callback=callback)

if __name__ == '__main__':
    setup(4, detector_event)
    try:
        while True:
            time.sleep(1)
    except Exception:
        GPIO.cleanup()

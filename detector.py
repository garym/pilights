#/usr/bin/env python3

from RPi import GPIO
import time

def detector_event(channel):
    value = GPIO.input(channel)
    print('This is an edge event callback.')
    print('  Edge detected on {}.'.format(channel))
    print('  Detector is {}.'.format('unblocked' if value else 'blocked'))

def setup(channel, callback):
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print('Initial state of detector is {}.'.format(
        'unblocked' if GPIO.input(channel) else 'blocked'))
    print('Waiting for detector events...')
    GPIO.add_event_detect(channel, GPIO.BOTH, callback=callback)

if __name__ == '__main__':
    detector = 4
    setup(detector, detector_event)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Cleaning up...')
        GPIO.cleanup()
        print('  done.')


STICK_LENGTH = 8
ARC_LENGTH = 15
INPUT_STREAM_START = 0
ARC1_START = INPUT_STREAM_START + STICK_LENGTH
ARC2_START = ARC1_START + ARC_LENGTH
ARC3_START = ARC2_START + ARC_LENGTH
ARC4_START = ARC3_START + ARC_LENGTH
OUTPUT_STREAM_START = ARC4_START + ARC_LENGTH

IN_STREAM = list(range(INPUT_STREAM_START,
                       INPUT_STREAM_START + STICK_LENGTH))
ARC1_PIXELS = list(range(ARC1_START,
                         ARC1_START + ARC_LENGTH))
ARC2_PIXELS = list(range(ARC2_START,
                         ARC2_START + ARC_LENGTH))
ARC3_PIXELS = list(range(ARC3_START,
                         ARC3_START + ARC_LENGTH))
ARC4_PIXELS = list(range(ARC4_START,
                         ARC4_START + ARC_LENGTH))
OUT_STREAM = list(range(OUTPUT_STREAM_START,
                        OUTPUT_STREAM_START + STICK_LENGTH))

TIMESTEP = 0.25

from collections import Counter


class State(object):
    def __init__(self):
        self.in_stream = self.init_counter(IN_STREAM)
        arc1 = self.init_counter(ARC1_PIXELS)
        arc2 = self.init_counter(ARC2_PIXELS)
        arc3 = self.init_counter(ARC3_PIXELS)
        arc4 = self.init_counter(ARC4_PIXELS)
        self.circle = arc1 + arc2 + arc3 + arc4
        self.out_stream = self.init_counter(OUT_STREAM)

    def init_counter(self, positions):
        return Counter({i: 0 for i in positions})

    def inject_pixel(self):
        self.in_stream

import argparse
from collections import deque
import logging
import sys
import time

from RPi import GPIO

logger = logging.getLogger()

try:
    import opc
except ImportError as e:
    logger.error(
        "Missing opc module. You may have forgotten to init submodules. "
        "See README.md for details."
    )
    sys.exit(1)


DEFAULT_SERVER = 'localhost:7890'
DEFAULT_DETECTOR_PIN = 4

track_state = deque([0] * (STICK_LENGTH + ARC_LENGTH * 4 + STICK_LENGTH))


def timestep():
    track_state[-1] = 0
    track_state.rotate()


def inject(channel):
    value = GPIO.input(channel)
    logger.debug('Edge event detected on {}'.format(channel))
    logger.debug(
        '    Detector is {}.'.format('unblocked' if value else 'blocked')
    )
    if not value:
        track_state[0] += 1


def render(client):
    pixels = [(255, 139, 57) if p else (0, 0, 0) for p in track_state]
    client.put_pixels(pixels)


def process_args():
    parser = argparse.ArgumentParser(
        description='A lightshow for a Made In Sheffield exhibit',
    )
    parser.add_argument(
        '-s', '--server', default=DEFAULT_SERVER,
        help='specify the fadecandy port',
    )
    parser.add_argument(
        '-d', '--detector_pin', default=DEFAULT_DETECTOR_PIN, type=int,
        help='specify GPIO pin for detection events',
    )
    return parser.parse_args()


def setup_fc(server):
    client = opc.Client(server)
    return client


def setup_gpio(channel, callback):
    GPIO.setmode(GPIO.BCM)
    try:
        GPIO.setwarnings(False)
    except AttributeError:
        logger.warning("Not using real GPIO module.")
    GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(channel, GPIO.BOTH, callback=callback)


def main(client):
    while True:
        timestep()
        render(client)
        time.sleep(TIMESTEP)


if __name__ == '__main__':
    args = process_args()
    client = setup_fc(args.server)
    setup_gpio(args.detector_pin, inject)
    main(client)

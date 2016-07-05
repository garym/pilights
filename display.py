import argparse
from collections import deque
import logging
import random
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


STICK_LENGTH = 8
ARC_LENGTH = 15

TIMESTEP = 0.25

DEFAULT_SERVER = 'localhost:7890'
DEFAULT_DETECTOR_PIN = 4

track_in_path = deque([0] * STICK_LENGTH)
track_circle_top_path = deque([0] * ARC_LENGTH)
track_circle_bottom_path = deque([0] * 3 * ARC_LENGTH)
track_out_path = deque([0] * STICK_LENGTH)

track_state = [0] * (STICK_LENGTH + ARC_LENGTH * 4 + STICK_LENGTH)

premesis_track_in_path = deque([0] * STICK_LENGTH)
premesis_track_circle_top_path = deque([0] * ARC_LENGTH)
premesis_track_circle_bottom_path = deque([0] * 3 * ARC_LENGTH)
premesis_track_out_path = deque([0] * STICK_LENGTH)

premesis_track_state = [0] * (STICK_LENGTH + ARC_LENGTH * 4 + STICK_LENGTH)

USER_TRACK_MAP_1 = {i: i for i in range(38)}

USER_TRACK_MAP_2 = {i: i for i in range(8)}
USER_TRACK_MAP_2.update({i + 8: 67 - i for i in range(30)})

BUILDING_TRACK_MAP_1 = {i: i + 23 for i in range(30)}
BUILDING_TRACK_MAP_1.update({i - 38: i for i in range(68, 76)})
BUILDING_TRACK_MAP_2 = {i: 22 - i for i in range(15)}
BUILDING_TRACK_MAP_2.update({i + 15: 67 - i for i in range(15)})
BUILDING_TRACK_MAP_2.update({i - 38: i for i in range(68, 76)})

empty_pixel_array = [(0, 0, 0)] * (2 * STICK_LENGTH + 4 * ARC_LENGTH)
global_pixel_array = []

class TrackLayer(object):
    def __init__(self, track_map, track_position, colour, is_building):
        self.track_map = track_map
        self.track_position = track_position
        self.colour = colour
        self.state = 255 if is_building else 0
        self.is_building = is_building

        self.real_position = track_map[track_position]

        self.track_state = deque([0] * 38)

    def inject(self):
        self.track_state[self.trac_position] += 1

    def decay(self):
        if self.state:
            self.state = int(self.state * 0.75)

    def set_high_state(self):
        self.state = 255

    def timestep(self):
        self.track_state.rotate()
        self.track_state[0] = 0

        if self.is_building:
            self.decay()
            if random.random() > 0.95:
                self.inject()

    def render_layer_track(self):
        for i, v in enumerate(self.track_state)
            if v:
                global_pixel_array[self.track_map[i]] = self.colour

    def render_building_state(self):
        global_pixel_array[self.track_map[self.track_position]] = (0, self.state, 0)


locations = [
    TrackLayer(BUILDING_TRACK_MAP_1,  7, (0, 200, 200), True),
    TrackLayer(BUILDING_TRACK_MAP_1,  22, (200, 0, 200), True),
    TrackLayer(BUILDING_TRACK_MAP_2,  7, (255, 0, 0), True),
    TrackLayer(BUILDING_TRACK_MAP_2,  22, (0, 0, 255), True),
]

user_tracks = [
    TrackLayer(USER_TRACK_MAP_1,  0, (255, 139, 57), False),
    TrackLayer(USER_TRACK_MAP_2,  0, (255, 139, 57), False),
]


def timestep():
    for track in user_tracks + locations:
        track.timestep()


def inject(channel):
    value = GPIO.input(channel)
    logger.debug('Edge event detected on {}'.format(channel))
    logger.debug(
        '    Detector is {}.'.format('unblocked' if value else 'blocked')
    )
    if not value:
        for track in user_tracks:
            track.inject()


def render(client):
    global_pixel_array.clear()
    global_pixel_array.extend(c for c in empty_pixel_array())
    for track in user_tracks + locations:
        track.render_layer_track()

    for track in locations:
        track.render_building_state()

    client.put_pixels(global_pixel_array)


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

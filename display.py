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

TIMESTEP = 0.05

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

USER_TRACK_MAP_1 = {i: p for (i, p) in enumerate(reversed(range(8, 16)))}
USER_TRACK_MAP_1.update({i: p for (i, p) in enumerate(range(46, 61), 8)})
USER_TRACK_MAP_1.update({i: p for (i, p) in enumerate(range(16, 31), 23)})

USER_TRACK_MAP_2 = {i: p for (i, p) in enumerate(reversed(range(8, 16)))}
USER_TRACK_MAP_2.update({i: p for (i, p) in enumerate(reversed(range(61, 76)), 8)})
USER_TRACK_MAP_2.update({i: p for (i, p) in enumerate(reversed(range(31, 46)), 23)})

BUILDING_TRACK_MAP_1 = {i: p for (i, p) in enumerate(range(61, 76))}
BUILDING_TRACK_MAP_1.update({i: p for (i, p) in enumerate(range(46, 61), 15)})
BUILDING_TRACK_MAP_1.update({i: p for (i, p) in enumerate(range(0, 8), 30)})

BUILDING_TRACK_MAP_2 = {i: p for (i, p) in enumerate(reversed(range(31, 46)))}
BUILDING_TRACK_MAP_2.update({i: p for (i, p) in enumerate(reversed(range(16, 31)), 15)})
BUILDING_TRACK_MAP_2.update({i: p for (i, p) in enumerate(range(0, 8), 30)})

empty_pixel_array = [(0, 0, 0)] * (2 * STICK_LENGTH + 4 * ARC_LENGTH)
global_pixel_array = []

class TrackLayer(object):
    def __init__(self, track_map, track_position, colour, is_building):
        self.track_map = track_map
        self.track_position = track_position
        self.colour = colour
        self.state_r, self.state_g, self.state_b = (0, 0, 0)
        if is_building:
            self.set_high_state()

        self.is_building = is_building

        self.real_position = track_map[track_position]

        self.track_state = deque([0] * 38)

    def inject(self):
        self.track_state[self.track_position] += 1

    def inject2(self):
        self.track_state[self.track_position] += 1
        self.track_state[self.track_position + 1] += 1
        self.track_state[self.track_position + 2] += 1

    def decay(self):
        startfactor = 0.999
        finishfactor = 0.95
        if self.state_r > 240:
            self.state_r = int(self.state_r * startfactor)
            self.state_g = int(self.state_g * startfactor)
            self.state_b = int(self.state_b * startfactor)
        if self.state_r > 40:
            self.state_r = int(self.state_r * finishfactor)
            self.state_g = int(self.state_g * finishfactor)
            self.state_b = int(self.state_b * finishfactor)

    def set_high_state(self):
        self.state_r = 255
        self.state_g = 139
        self.state_b = 57

    def timestep(self):
        self.track_state.rotate()
        self.track_state[0] = 0

        if self.is_building:
            self.decay()
            if random.random() > 0.95:
                self.inject()

    def render_layer_track(self):
        for i, v in enumerate(self.track_state):
            if v:
                try:
                    global_pixel_array[self.track_map[i]] = self.colour
                except KeyError:
                    import pdb; pdb.set_trace()
                    print(global_pixel_array)

    def render_building_state(self):
        global_pixel_array[self.track_map[self.track_position]] = (self.state_r, self.state_g, self.state_b)


locations = [
    TrackLayer(BUILDING_TRACK_MAP_1,  7, (0, 200, 200), True),
    TrackLayer(BUILDING_TRACK_MAP_1,  22, (200, 0, 200), True),
    TrackLayer(BUILDING_TRACK_MAP_2,  7, (0, 255, 0), True),
    TrackLayer(BUILDING_TRACK_MAP_2,  22, (0, 0, 255), True),
]

user_tracks = [
    TrackLayer(USER_TRACK_MAP_1,  0, (255, 139, 57), False),
    TrackLayer(USER_TRACK_MAP_2,  0, (255, 139, 57), False),
]


def timestep():
    for track in user_tracks + locations:
        track.timestep()
    for location in locations:
        for track in user_tracks:
            for pos, translated in track.track_map.items():
                if translated == location.real_position and track.track_state[pos]:
                    location.set_high_state()
                    break


def inject(channel):
    value = GPIO.input(channel)
    logger.debug('Edge event detected on {}'.format(channel))
    logger.debug(
        '    Detector is {}.'.format('unblocked' if value else 'blocked')
    )
    if not value:
        for track in user_tracks:
            track.inject2()


def render(client):
    global_pixel_array.clear()
    global_pixel_array.extend(c for c in empty_pixel_array)
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

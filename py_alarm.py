'''Simple terminal pomodoro timer.
By default a 25 minute, then 5 minute timer on loop.
'''
from itertools import cycle
import argparse
import shutil
import pyglet
import time
import os

REFRESH_RATE = 0.05
DEFAULT_SOUNDPATH_RELATIVE_TO_FILE_DIR = (
    'data/siren_noise_soundbible_shorter_fadeout.wav'
)

FILE_DIR = os.path.dirname(__file__)
DEFAULT_SOUNDPATH = (
    os.path.join(FILE_DIR, DEFAULT_SOUNDPATH_RELATIVE_TO_FILE_DIR)
)
TIME_FORMAT = '{:02d}:{:02d} / {:02d}:00'


def get_terminal_width():
    return shutil.get_terminal_size((80, 20)).columns


TERMINAL_WIDTH = get_terminal_width()


class CycleAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        setattr(args, self.dest, cycle(values))


def build_parser():

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        'countdowns', type=int, nargs='*',
        action=CycleAction,
        default=cycle((25, 5)),
        help='Cycle through countdown of this many minutes.'
    )

    parser.add_argument(
        '--sound-path', type=str,
        default=DEFAULT_SOUNDPATH,
        help='Path to alarm sound.'
    )

    return parser


def run_sound(sound_path):
    sound = pyglet.resource.media(sound_path)
    sound.play()

    # This is kind of an abuse of pyglet
    pyglet.clock.schedule_once(lambda x: pyglet.app.exit(), sound.duration)
    pyglet.app.run()


def minutes_seconds_elapsed(elapsed):
    minutes, seconds = divmod(elapsed, 60)
    _, minutes = divmod(minutes, 60)

    return int(minutes), int(seconds)


def print_time(minutes, seconds, total_minutes):
    print('\r', end='')
    time_str = TIME_FORMAT.format(minutes, seconds, total_minutes)
    time_str = time_str.center(TERMINAL_WIDTH)
    print(time_str, end='')


def clear_if_changed(changed):
    if changed:
        os.system('clear')


def countdown(minutes_total):
    global TERMINAL_WIDTH

    upper_limit = minutes_total * 60
    start_time = time.time()
    while True:
        elapsed = time.time() - start_time
        timer_numbers = (*minutes_seconds_elapsed(elapsed), minutes_total)

        current_width = get_terminal_width()
        width_changed = current_width != TERMINAL_WIDTH
        TERMINAL_WIDTH = current_width
        clear_if_changed(width_changed)

        print_time(*timer_numbers)
        time.sleep(REFRESH_RATE)

        if width_changed:
            os.system('clear')

        if elapsed >= upper_limit:
            print()
            break


def main():
    args = build_parser().parse_args()
    assert os.path.isfile(args.sound_path), (
        '{} is not a file.'.format(args.sound_path)
    )

    try:
        while True:
            countdown(next(args.countdowns))
            run_sound(args.sound_path)
            input('Press return to reset'.center(TERMINAL_WIDTH))
    except KeyboardInterrupt:
        print('', end='\r')
        print()
        print('Goodbye!'.center(TERMINAL_WIDTH))

        # Hack to stop strange callback happening on exit
        pyglet.media.drivers.get_audio_driver().delete()
    except StopIteration:
        # Shouldn't actually get here, because of defaults in argparse.
        print('Need to have some countdowns!'.center(TERMINAL_WIDTH))


if __name__ == '__main__':
    main()

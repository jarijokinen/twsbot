import argparse
import curses
import time

from . import __version__
from twsbot.core import Core
from twsbot.utils import buffer

def curses_main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)

    core = Core()
    core.start()
    core.fetch_historical_data('AAPL')

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f'twsbot {__version__}', curses.A_REVERSE)

        for idx, line in enumerate(list(buffer.queue)[-30:]):
            if idx < curses.LINES - 2:
                stdscr.addstr(idx + 2, 0, line)

        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            core.stop()
            break

        time.sleep(0.1)

def main():
    parser = argparse.ArgumentParser(
        description='twsbot CLI',
        prog='twsbot'
    )
    parser.add_argument(
        '-v',
        '--version',
        action='version', 
        version=f'%(prog)s {__version__}'
    )
    args = parser.parse_args()

    curses.wrapper(curses_main)

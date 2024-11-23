import argparse
import curses

from . import __version__

def curses_main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    
    stdscr.clear()
    stdscr.addstr(0, 0, f'twsbot {__version__}', curses.A_REVERSE)
    
    while True:
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            break

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

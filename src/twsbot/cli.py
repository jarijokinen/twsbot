import argparse
import curses
import numpy as np
import talib
import time

from . import __version__
from twsbot.core import Core
from twsbot.utils import bars, buffer

def curses_main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)

    core = Core()
    core.start()
    core.fetch_historical_data('AAPL')

    ema_a = 0.0
    ema_b = 0.0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f'twsbot {__version__}', curses.A_REVERSE)
    
        # Calculate EMAs

        close_prices = [bar.close for bar in list(bars.queue)[-20:]]
        close_prices_np = np.array(close_prices)

        if len(close_prices_np) >= 20:
            ema_a = talib.EMA(close_prices_np, timeperiod=9)[-1]
            ema_b = talib.EMA(close_prices_np, timeperiod=20)[-1]

        stdscr.addstr(0, 20, f'EMA9: {ema_a:.2f}  EMA20: {ema_b:.2f}')

        # Output buffer to screen

        for idx, line in enumerate(list(buffer.queue)[-30:]):
            if idx < curses.LINES - 2:
                stdscr.addstr(idx + 2, 0, line)

        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            core.stop()
            break

        time.sleep(1.0)

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

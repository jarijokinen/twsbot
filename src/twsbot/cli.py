import argparse
import curses
import time

from . import __version__
from twsbot.core import Core
from twsbot.utils import buffer

def curses_main(stdscr, symbol):
    curses.curs_set(0)
    stdscr.nodelay(1)

    core = Core()
    core.start()
    core.fetch_historical_data(symbol)

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f'twsbot {__version__}', curses.A_REVERSE)
        stdscr.addstr(2, 0,
            f'EMA9: {core.ema9:<10.2f} EMA20: {core.ema20:<10.2f} '
            f'ADX14: {core.adx14:<10.2f} '
            f'ATR14: {core.atr14:<10.2f} '
            f'Volume: {core.volume_trend}')
        stdscr.addstr(3, 0,
            f'Vol: {core.volume:<10.2f} '
            f'VMA14: {core.vma14:<10.2f} '
            f'Close: {core.close:<10.2f} '
            f'Bandwidth: {core.bb_bandwidth} '
            f'Consolidation: {core.in_consolidation} ')

        for i, line in enumerate(buffer):
            if i <= curses.LINES - 5:
                stdscr.addstr(i + 5, 0, line)

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
    parser.add_argument(
        'symbol',
        type=str,
        help='The stock symbol (e.g., AAPL, GOOGL, NVDA)'
    )
    args = parser.parse_args()

    curses.wrapper(lambda stdscr: curses_main(stdscr, args.symbol.upper()))

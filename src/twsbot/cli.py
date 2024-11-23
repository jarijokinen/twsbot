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

    # Indicators

    ema9 = 0.0
    ema20 = 0.0
    adx14 = 0.0
    adx14_plus = 0.0
    adx14_minus = 0.0

    # Signals

    buy_signal = 0.0
    sell_signal = 0.0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f'twsbot {__version__}', curses.A_REVERSE)
        
        high_prices = [bar.high for bar in list(bars.queue)[-40:]]
        low_prices = [bar.low for bar in list(bars.queue)[-40:]]
        close_prices = [bar.close for bar in list(bars.queue)[-40:]]

        high_prices_np = np.array(high_prices)
        low_prices_np = np.array(low_prices)
        close_prices_np = np.array(close_prices)
        
        # Calculate EMAs

        if len(close_prices_np) >= 20:
            ema9 = talib.EMA(close_prices_np, timeperiod=9)[-1]
            ema20 = talib.EMA(close_prices_np, timeperiod=20)[-1]

        stdscr.addstr(0, 20, f'EMA9: {ema9:.2f}  EMA20: {ema20:.2f}')

        # Calculate ADX

        if len(high_prices_np) >= 14 * 2:
            adx = talib.ADX(
                high_prices_np, 
                low_prices_np,
                close_prices_np, 
                timeperiod=14
            )
            adx14 = adx[-1]

            adx_plus = talib.PLUS_DI(
                high_prices_np, 
                low_prices_np,
                close_prices_np, 
                timeperiod=14
            )
            adx14_plus = adx_plus[-1]

            adx_minus = talib.MINUS_DI(
                high_prices_np, 
                low_prices_np,
                close_prices_np, 
                timeperiod=14
            )
            adx14_minus = adx_minus[-1]
 
        stdscr.addstr(1, 20, 
            f'ADX: {adx14:.2f}  ADX+: {adx14_plus:.2f}  ADX-: {adx14_minus:.2f}'
        )

        # Calculate signals

        # EMA crossover

        if ema9 > ema20:
            buy_signal = 1

        if ema9 < ema20:
            sell_signal = 1
        
        # ADX strength and trend direction

        if adx14 > 25:
            if adx14_plus > adx14_minus:
                buy_signal += 1

            if adx14_plus < adx14_minus:
                sell_signal += 1

        # Output signals

        stdscr.addstr(1, 0, f'BUY: {buy_signal:.2f}  SELL: {sell_signal:.2f}')

        # Output buffer

        for idx, line in enumerate(list(buffer.queue)[-30:]):
            if idx < curses.LINES - 3:
                stdscr.addstr(idx + 3, 0, line)

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

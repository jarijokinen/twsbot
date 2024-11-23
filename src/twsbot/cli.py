import argparse
import curses
import numpy as np
import talib
import time

from . import __version__
from twsbot.core import Core
from twsbot.utils import bars, buffer

def curses_main(stdscr, symbol):
    curses.curs_set(0)
    stdscr.nodelay(1)

    core = Core()
    core.start()
    core.fetch_historical_data(symbol)

    # Indicators

    ema9 = 0.0
    ema20 = 0.0
    adx14 = 0.0
    adx14_plus = 0.0
    adx14_minus = 0.0

    atr14 = 0.0

    # Signals

    buy_signal = 0.0
    sell_signal = 0.0

    # Position

    sl = 0.0

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f'twsbot {__version__}', curses.A_REVERSE)
        
        highs = [bar.high for bar in list(bars.queue)[-40:]]
        lows = [bar.low for bar in list(bars.queue)[-40:]]
        closes = [bar.close for bar in list(bars.queue)[-40:]]

        highs_np = np.array(highs)
        lows_np = np.array(lows)
        closes_np = np.array(closes)
        
        # Calculate EMAs

        if len(closes_np) >= 20:
            ema9 = talib.EMA(closes_np, timeperiod=9)[-1]
            ema20 = talib.EMA(closes_np, timeperiod=20)[-1]

        # Calculate ADX

        if len(highs_np) >= 14 * 2:
            adx = talib.ADX(
                highs_np, 
                lows_np,
                closes_np, 
                timeperiod=14
            )
            adx14 = adx[-1]

            adx_plus = talib.PLUS_DI(
                highs_np, 
                lows_np,
                closes_np, 
                timeperiod=14
            )
            adx14_plus = adx_plus[-1]

            adx_minus = talib.MINUS_DI(
                highs_np, 
                lows_np,
                closes_np, 
                timeperiod=14
            )
            adx14_minus = adx_minus[-1]

        # Calculate ATR

        if len(highs_np) >= 14:
            atr = talib.ATR(
                highs_np, 
                lows_np,
                closes_np, 
                timeperiod=14
            )
            atr14 = atr[-1]

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

        # Trailing stop-loss calculation

        if len(lows) >= 1:
            if buy_signal > sell_signal:
                new_sl = lows[-1] - atr14 * 2.0
            else:
                new_sl = highs[-1] + atr14 * 2.0
            if new_sl > sl:
                sl = new_sl
        
        # Output indicators and signals

        stdscr.addstr(0, 14, f'EMA9: {ema9:.2f}')
        stdscr.addstr(0, 28, f'EMA20: {ema20:.2f}')
        stdscr.addstr(0, 44, f'ADX: {adx14:.2f}')
        stdscr.addstr(0, 56, f'ADX+: {adx14_plus:.2f}')
        stdscr.addstr(0, 70, f'ADX-: {adx14_minus:.2f}')
        stdscr.addstr(1, 0, f'{symbol}')
        stdscr.addstr(1, 14, f'ATR:  {atr14:.2f}')
        stdscr.addstr(1, 28, f'SL:    {sl:.2f}')
        stdscr.addstr(1, 44, f'BUY: {buy_signal:.2f}')
        stdscr.addstr(1, 56, f'SELL: {sell_signal:.2f}')

        # Output buffer

        for idx, line in enumerate(list(buffer.queue)[-30:]):
            if idx < curses.LINES - 4:
                stdscr.addstr(idx + 4, 0, line)

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
    parser.add_argument(
        'symbol',
        type=str,
        help='The stock symbol (e.g., AAPL, GOOGL, NVDA)'
    )
    args = parser.parse_args()

    curses.wrapper(lambda stdscr: curses_main(stdscr, args.symbol))

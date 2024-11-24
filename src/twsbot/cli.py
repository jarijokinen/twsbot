import argparse
import curses
import numpy as np
import talib
import time

from . import __version__
from twsbot.account import Account
from twsbot.core import Core
from twsbot.utils import bars, buffer

def curses_main(stdscr, symbol):
    curses.curs_set(0)
    stdscr.nodelay(1)

    account = Account()

    core = Core()
    core.start()
    core.fetch_historical_data(symbol)
    
    h, l, c = 0.0, 0.0, 0.0

    # Indicators

    ema9 = 0.0
    ema20 = 0.0
    adx14 = 0.0
    adx14_plus = 0.0
    adx14_minus = 0.0

    atr14 = 0.0

    ema_count = 0
    adx_count = 0

    # Position

    sl = 0.0
    tp = False

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, f'twsbot {__version__}', curses.A_REVERSE)
    
        buy_signal = 0.0
        sell_signal = 0.0
        
        highs = [bar.high for bar in list(bars.queue)[-40:]]
        lows = [bar.low for bar in list(bars.queue)[-40:]]
        closes = [bar.close for bar in list(bars.queue)[-40:]]

        highs_np = np.array(highs)
        lows_np = np.array(lows)
        closes_np = np.array(closes)

        if len(closes) > 0:
            h = highs[-1]
            l = lows[-1]
            c = closes[-1]

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
            ema_count += 1
            if ema_count >= 4:
                ema_count = 4
                buy_signal += 1

        if ema9 < ema20:
            ema_count -= 1
            if ema_count <= -4:
                ema_count = -4
                sell_signal += 1
        
        # ADX strength and trend direction

        if adx14 > 25:
            if adx14_plus > adx14_minus:
                adx_count += 1
                if adx_count >= 4:
                    adx_count = 4
                    buy_signal += adx14 // 20 

            if adx14_plus < adx14_minus:
                adx_count -= 1
                if adx_count <= -4:
                    adx_count = -4
                    sell_signal += adx14 // 20
        
        # Trailing stop-loss calculation

        if l > 0:
            if tp is False:
                if account.position == 'long':
                    new_sl = l - (atr14 * 1.3)
                    if new_sl > sl:
                        sl = new_sl
                elif account.position == 'short':
                    new_sl = h + (atr14 * 1.3)
                    if new_sl < sl:
                        sl = new_sl
                else:
                    sl = 0.0
            else:
                if account.position == 'long':
                    new_sl = c - (atr14 * 1.2)
                    if new_sl > sl:
                        sl = new_sl
                elif account.position == 'short':
                    new_sl = c + (atr14 * 1.2)
                    if new_sl < sl:
                        sl = new_sl
                else:
                    sl = 0.0
         
        # Take profit calculation

        if account.position == 'long':
            if (l - account.current_trade['bought_at']) * account.qty > 30:
                tp = True
        elif account.position == 'short':
            if (account.current_trade['sold_at'] - h) * account.qty > 30:
                tp = True

        # Position management
        
        if account.position == 'long' and l <= sl and sl > 0:
            account.sell(l)
            buffer.append(f'SL SELL {account.qty} @ {l:.2f}')
            tp = False
            sl = 0.0
        elif account.position == 'short' and h >= sl and sl > 0:
            account.cover(h)
            buffer.append(f'SL COVER {account.qty} @ {h:.2f}')
            tp = False
            sl = 0.0
        elif buy_signal > sell_signal and buy_signal > 2 and c > 0:
            if account.position is None:
                account.buy(c)
                buffer.append(f'BUY {account.qty} @ {c:.2f}')
                sl = l - (atr14 * 2.0)
                tp = False
            elif account.position == 'short':
                account.cover(c)
                buffer.append(f'COVER {account.qty} @ {c:.2f}')
                tp = False
        elif buy_signal < sell_signal and sell_signal > 2 and c > 0:
            if account.position is None:
                account.short(c)
                buffer.append(f'SHORT {account.qty} @ {c:.2f}')
                sl = h + (atr14 * 2.0)
                tp = False
            elif account.position == 'long':
                account.sell(c)
                buffer.append(f'SELL {account.qty} @ {c:.2f}')
                tp = False
 
        # Output indicators and signals

        stdscr.addstr(0, 16, f'EMA9: {ema9:.2f}')
        stdscr.addstr(0, 30, f'EMA20: {ema20:.2f}')
        stdscr.addstr(0, 46, f'ADX: {adx14:.2f}')
        stdscr.addstr(0, 58, f'ADX+: {adx14_plus:.2f}')
        stdscr.addstr(0, 71, f'ADX-: {adx14_minus:.2f}')
        stdscr.addstr(1, 0, f'{symbol}')
        stdscr.addstr(1, 16, f'ATR:  {atr14:.2f}')
        stdscr.addstr(1, 30, f'SL:    {sl:.2f}')
        stdscr.addstr(1, 46, f'BUY: {buy_signal:.2f}')
        stdscr.addstr(1, 58, f'SELL: {sell_signal:.2f}')
        stdscr.addstr(2, 0, f'Cash: {account.cash:.2f}')
        stdscr.addstr(2, 16, f'EMA: {ema_count}')
        stdscr.addstr(2, 30, f'ADX: {adx_count}')

        # Output buffer

        for idx, line in enumerate(buffer):
            if idx < curses.LINES - 4:
                stdscr.addstr(idx + 4, 0, line)

        # Output current position
        
        if curses.LINES > 23:
            stdscr.addstr(21, 0, f'Current Position', curses.A_REVERSE)

            if account.position == 'long':
                pl = (c - account.current_trade['bought_at']) * account.qty \
                    - account.fee
                stdscr.addstr(23, 0, 
                    f'LONG  {account.qty} @ '
                    f'{account.current_trade["bought_at"]}'
                    f' -> {c:.2f} PL: {pl:.2f}'
                )
            elif account.position == 'short':
                pl = (account.current_trade['sold_at'] - c) * account.qty \
                    - account.fee
                stdscr.addstr(23, 0, 
                    f'SHORT {account.qty} @ {account.current_trade["sold_at"]}'
                    f' -> {c:.2f} PL: {pl:.2f}')

        # Output trade log
        
        stdscr.addstr(25, 0, f'Trade Log', curses.A_REVERSE)

        for idx, trade in enumerate(account.trades[-10:]):
            if idx < curses.LINES - 27:
                if trade['position'] == 'long':
                    pl = (trade['sold_at'] - trade['bought_at']) \
                        * trade['qty'] - account.fee
                    stdscr.addstr(idx + 27, 0, 
                        f'LONG  {trade["qty"]} @ {trade["bought_at"]:.2f}'
                        f' -> {trade["sold_at"]:.2f} PL: {pl:.2f}')
                elif trade['position'] == 'short':
                    pl = (trade['sold_at'] - trade['bought_at']) \
                        * trade['qty'] - account.fee
                    stdscr.addstr(idx + 27, 0,
                        f'SHORT {trade["qty"]} @ {trade["sold_at"]:.2f}'
                        f' -> {trade["bought_at"]:.2f} PL: {pl:.2f}')

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

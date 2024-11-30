import time
import threading

from twsbot.twsapi import TwsApi
from twsbot.utils import buffer, bars

class Core:
    def __init__(self):
        self.twsapi = TwsApi()
        self.contract = None
        self.adx14 = 0.0
        self.adx14_plus = 0.0
        self.adx14_minus = 0.0
        self.atr14 = 0.0
        self.ema9 = 0.0
        self.ema20 = 0.0

    def start(self):    
        buffer.append('Connecting to TWS API...')
        self.twsapi.connect('127.0.0.1', 7496, clientId=1)

        while not self.twsapi.isConnected():
            time.sleep(1)
            break

        buffer.append('Connected to TWS API successfully!')
        time.sleep(1)
        threading.Thread(target=self._twsapi_worker, daemon=True).start()

    def stop(self):
        self.twsapi.disconnect()

    def fetch_historical_data(self, symbol):
        self.contract = self.twsapi.create_contract(symbol)
        self.twsapi.reqHistoricalData(
            1,
            self.contract,
            '',
            '1 D',
            '5 secs',
            'TRADES',
            1,
            2,
            False,
            []
        )
    
    def _data_worker(self):
        global buffer

        account = Account()
        
        h, l, c = 0.0, 0.0, 0.0

        # Indicators

        ema_count = 0
        adx_count = 0

        # Position

        sl = 0.0
        tp = False

        while True:
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
                self.ema9 = talib.EMA(closes_np, timeperiod=9)[-1]
                self.ema20 = talib.EMA(closes_np, timeperiod=20)[-1]

            # Calculate ADX

            if len(highs_np) >= 14 * 2:
                adx = talib.ADX(
                    highs_np, 
                    lows_np,
                    closes_np, 
                    timeperiod=14
                )
                self.adx14 = adx[-1]

                adx_plus = talib.PLUS_DI(
                    highs_np, 
                    lows_np,
                    closes_np, 
                    timeperiod=14
                )
                self.adx14_plus = adx_plus[-1]

                adx_minus = talib.MINUS_DI(
                    highs_np, 
                    lows_np,
                    closes_np, 
                    timeperiod=14
                )
                self.adx14_minus = adx_minus[-1]

            # Calculate ATR

            if len(highs_np) >= 14:
                atr = talib.ATR(
                    highs_np, 
                    lows_np,
                    closes_np, 
                    timeperiod=14
                )
                self.atr14 = atr[-1]

            # Calculate signals

            # EMA crossover

            if self.ema9 > self.ema20:
                ema_count += 1
                if ema_count >= 4:
                    ema_count = 4
                    buy_signal += 1

            if self.ema9 < self.ema20:
                ema_count -= 1
                if ema_count <= -4:
                    ema_count = -4
                    sell_signal += 1
            
            # ADX strength and trend direction

            if self.adx14 > 25:
                if self.adx14_plus > self.adx14_minus:
                    adx_count += 1
                    if adx_count >= 4:
                        adx_count = 4
                        buy_signal += self.adx14 // 20 

                if self.adx14_plus < self.adx14_minus:
                    adx_count -= 1
                    if adx_count <= -4:
                        adx_count = -4
                        sell_signal += self.adx14 // 20
            
            # Trailing stop-loss calculation

            if l > 0:
                if tp is False:
                    if account.position == 'long':
                        new_sl = l - (self.atr14 * 1.8)
                        if new_sl > sl:
                            sl = new_sl
                    elif account.position == 'short':
                        new_sl = h + (self.atr14 * 1.8)
                        if new_sl < sl:
                            sl = new_sl
                    else:
                        sl = 0.0
                else:
                    if account.position == 'long':
                        new_sl = c - (self.atr14 * 1.2)
                        if new_sl > sl:
                            sl = new_sl
                    elif account.position == 'short':
                        new_sl = c + (self.atr14 * 1.2)
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

    def _twsapi_worker(self):
        self.twsapi.run()

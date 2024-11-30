import talib
import threading
import time

from twsbot.twsapi import TwsApi
from twsbot.utils import buffer, get_bars

class Core:
    def __init__(self):
        self.twsapi = TwsApi()
        self.contract = None

        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []

        self.volume = 0.0
        self.close = 0.0

        self.adx14 = 0.0
        self.adx14_plus = 0.0
        self.adx14_minus = 0.0
        self.atr14 = 0.0
        self.ema9 = 0.0
        self.ema20 = 0.0
        self.vma14 = 0.0
        self.bb_upper = 0.0
        self.bb_middle = 0.0
        self.bb_lower = 0.0
        self.bb_bandwidth = 0.0
        self.kc_upper = 0.0
        self.kc_lower = 0.0

        self.ema_trend = 'neutral'
        self.adx_trend = 'neutral'
        self.volume_trend = 'neutral'
        self.kc_breakout = 'neutral'

        self.in_consolidation = False

    def start(self):    
        buffer.append('Connecting to TWS API...')
        self.twsapi.connect('127.0.0.1', 7496, clientId=1)

        while not self.twsapi.isConnected():
            time.sleep(1)
            break

        buffer.append('Connected to TWS API successfully!')
        time.sleep(1)
        threading.Thread(target=self._twsapi_worker, daemon=True).start()
        threading.Thread(target=self._data_worker, daemon=True).start()
        threading.Thread(target=self._indicator_worker, daemon=True).start()
        threading.Thread(target=self._signal_worker, daemon=True).start()
        threading.Thread(target=self._strategy_worker, daemon=True).start()

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
            True,
            []
        )

    def _data_worker(self):
        while True:
            self.highs = get_bars('high')
            self.lows = get_bars('low')
            self.closes = get_bars('close')
            self.volumes = get_bars('volume')

            self.close = self.closes[-1]
            self.volume = self.volumes[-1]
    
            time.sleep(1)

    def _indicator_worker(self):
        while True:

            # EMA

            self.ema9 = talib.EMA(self.closes, timeperiod=9)[-1]
            self.ema20 = talib.EMA(self.closes, timeperiod=20)[-1]
            
            # ADX

            self.adx14 = talib.ADX(
                self.highs, 
                self.lows, 
                self.closes, 
                timeperiod=14
            )[-1]
            self.adx14_plus = talib.PLUS_DI(
                self.highs, 
                self.lows,
                self.closes, 
                timeperiod=14
            )[-1]
            self.adx14_minus = talib.MINUS_DI(
                self.highs, 
                self.lows,
                self.closes, 
                timeperiod=14
            )[-1]

            # ATR

            self.atr14 = talib.ATR(
                self.highs, 
                self.lows, 
                self.closes, 
                timeperiod=14
            )[-1]

            # VMA

            self.vma14 = talib.SMA(self.volumes, timeperiod=14)[-1]
 
            # Bollinger Bands

            upper, middle, lower = talib.BBANDS(
                self.closes,
                timeperiod=20,
                nbdevup=2,
                nbdevdn=2,
                matype=0
            )
            self.bb_upper = upper[-1]
            self.bb_middle = middle[-1]
            self.bb_lower = lower[-1]
            self.bb_bandwidth = (self.bb_upper - self.bb_lower) / self.bb_middle

            # Keltner Channels
            
            self.kc_upper = self.ema20 + (self.atr14 * 1.5)
            self.kc_lower = self.ema20 - (self.atr14 * 1.5)

            time.sleep(1)
            
    def _signal_worker(self):
        while True:

            # EMA crossover

            if self.ema9 > self.ema20:
                self.ema_trend = 'bull'

            if self.ema9 < self.ema20:
                self.ema_trend = 'bear'
                pass

            # ADX trend
            
            if self.adx14 > 25:
                if self.adx14_plus > self.adx14_minus:
                    self.adx_trend = 'bull'
                elif self.adx14_plus < self.adx14_minus:
                    self.adx_trend = 'bear'
                else:
                    self.adx_trend = 'neutral'
            
            # Volume trend

            if self.volume > self.vma14 * 1.5:
                self.volume_trend = 'strong'
            elif self.volume < self.vma14 * 1.5:
                self.volume_trend = 'weak'
            else:
                self.volume_trend = 'neutral'

            # Consolidation

            if self.bb_bandwidth < 0.01 and self.atr14 < 0.5 and self.adx14 < 20:
                self.in_consolidation = True
            else:
                self.in_consolidation = False
            
            # Keltner breakout

            if self.volume_trend == 'strong' and self.close > self.kc_upper:
                self.kc_breakout = 'bull'
            elif self.volume_trend == 'strong' and self.close < self.kc_lower:
                self.kc_breakout = 'bear'
            else:
                self.kc_breakout = 'neutral'
            
            time.sleep(1)
    
    def _strategy_worker(self):
        while True:
            if self.ema_trend == 'bull' and self.adx_trend == 'bull':
                pass

            time.sleep(1)

    def _twsapi_worker(self):
        self.twsapi.run()

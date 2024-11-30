import time
import threading

from twsbot.twsapi import TwsApi
from twsbot.utils import buffer

class Core:
    def __init__(self):
        self.twsapi = TwsApi()
        self.contract = None

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
            1,
            False,
            []
        )

    def _twsapi_worker(self):
        self.twsapi.run()

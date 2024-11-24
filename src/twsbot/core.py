import time
import threading

from twsbot.twsapi import TWSAPI
from twsbot.utils import buffer

class Core:
    def __init__(self):
        self.twsapi = TWSAPI()

    def start(self):    
        buffer.put('Connecting to TWS...')
        self.twsapi.connect('127.0.0.1', 7496, clientId=1)

        while True:
            if self.twsapi.isConnected():
                buffer.put('Connected to TWS successfully')
                time.sleep(1)
                threading.Thread(target=self.twsapi_worker, daemon=True).start()
                break

    def stop(self):
        self.twsapi.disconnect()

    def fetch_historical_data(self, symbol):
        self.contract = self.twsapi.create_contract(symbol)
        threading.Thread(target=self.historical_data_worker, daemon=True).start()

    def historical_data_worker(self):
        self.twsapi.reqHistoricalData(
            1,
            self.contract,
            '',
            '1 D',
            '1 min',
            'TRADES',
            1,
            1,
            False,
            []
        )
    
    def twsapi_worker(self):
        self.twsapi.run()

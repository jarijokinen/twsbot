from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from twsbot.utils import append_bar_data, buffer

import time

class TwsApi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString):
        buffer.append(f'Error: {reqId} {errorCode} {errorString}')

    def historicalData(self, reqId, bar):
        append_bar_data(bar)
        time.sleep(0.1)

    def create_contract(self, symbol):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        return contract

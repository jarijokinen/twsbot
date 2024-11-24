from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from twsbot.utils import bars, buffer

class TWSAPI(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    def error(self, reqId, errorCode, errorString):
        buffer.append(f'Error: {reqId} {errorCode} {errorString}')

    def historicalData(self, reqId, bar):
        bars.put(bar)
        buffer.append(
            f'{bar.date} -- O: {bar.open:.2f} H: {bar.high:.2f} '
            f'L: {bar.low:.2f} C: {bar.close:.2f} V: {bar.volume}'
        )

    def create_contract(self, symbol):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        return contract

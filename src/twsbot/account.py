class Account:
    def __init__(self):
        self.cash = 100000.00
        self.fee = 1.00
        self.qty = 100
        self.position = None
        self.trades = []
        self.current_trade = None

    def buy(self, price):
        self.cash -= (price * self.qty) + self.fee
        self.position = 'long'
        self.current_trade = {
            'bought_at': price,
            'sold_at': None,
            'qty': self.qty,
            'position': self.position
        }

    def sell(self, price):
        self.cash += (price * self.qty) - self.fee
        self.position = None
        self.current_trade['sold_at'] = price
        self.trades.append(self.current_trade)

    def short(self, price):
        self.cash += (price * self.qty) - self.fee
        self.position = 'short'
        self.current_trade = {
            'bought_at': None,
            'sold_at': price,
            'qty': self.qty,
            'position': self.position
        }

    def cover(self, price):
        self.cash -= (price * self.qty) + self.fee
        self.position = None
        self.current_trade['bought_at'] = price
        self.trades.append(self.current_trade)

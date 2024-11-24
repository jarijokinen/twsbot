class Account:
    def __init__(self):
        self.cash = 100000.00
        self.fee = 1.00
        self.qty = 100
        self.position = None

    def buy(self, price):
        self.cash -= (price * self.qty) + self.fee
        self.position = 'long'

    def sell(self, price):
        self.cash += (price * self.qty) - self.fee
        self.position = None

    def short(self, price):
        self.cash += (price * self.qty) - self.fee
        self.position = 'short'

    def cover(self, price):
        self.cash -= (price * self.qty) + self.fee
        self.position = None

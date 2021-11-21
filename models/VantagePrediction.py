class VantagePrediction:
    def __init__(self, symbol: str, category: str, plow: int, phigh: int):
        self.symbol = symbol
        self.category = category
        self.plow = plow
        self.phigh = phigh
        self.bought = False
        self.limitbuy = (self.phigh + self.plow) / 2

    def setBought(self):
        self.bought = True
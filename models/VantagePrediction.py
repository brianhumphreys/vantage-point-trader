from tools.bcolors import bcolors

class VantagePrediction:
    def __init__(self, symbol: str, category: str, plow: int, phigh: int, openprice: int):
        self.symbol = symbol
        self.category = category
        self.plow = plow
        self.phigh = phigh
        self.bought = False
        self.limitbuy = (self.phigh + self.plow) / 2
        self.openprice = openprice
        self.onepercentdrop = self.openprice * 0.995
        self.initialentry = False

        if(self.plow < self.onepercentdrop):
            print(bcolors.OKBLUE + 'PLOW' + bcolors.ENDC)
        else:
            print(bcolors.OKGREEN + 'DROP' + bcolors.ENDC)

    def setBought(self):
        self.bought = True
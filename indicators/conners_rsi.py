import backtrader as bt

class Streak(bt.ind.PeriodN):
    '''
    Keeps a counter of the current upwards/downwards/neutral streak
    '''
    lines = ('streak',)
    params = dict(period=2)  # need prev/cur days (2) for comparisons

    curstreak = 0

    def next(self):
        d0, d1 = self.data[0], self.data[-1]
        # print(2)

        if d0 > d1:
        #     print(3)
            self.l.streak[0] = self.curstreak = max(1, self.curstreak + 1)
        elif d0 < d1:
        #     print(4)
            self.l.streak[0] = self.curstreak = min(-1, self.curstreak - 1)
        else:
            self.l.streak[0] = self.curstreak = 0
        # print(6)


class ConnorsRSI(bt.Indicator):
    '''
    Calculates the ConnorsRSI as:
        - (RSI(per_rsi) + RSI(Streak, per_streak) + PctRank(per_rank)) / 3
    '''
    lines = ('crsi',)
    params = dict(prsi=3, pstreak=2, prank=100)

    def __init__(self, prsi, pstreak, prank):
        self.p.prsi = prsi
        self.p.pstreak = pstreak
        self.p.prank = prank
        # Calculate the components
        rsi = bt.ind.RSI_Safe(self.data, period=self.p.prsi)

        streak = Streak(self.data)
        rsi_streak = bt.ind.RSI_Safe(streak, period=self.p.pstreak)

        prank = bt.ind.PercentRank(self.data, period=self.p.prank)

        # # Apply the formula
        self.l.crsi = (prank + rsi + rsi_streak) / 3.0
        # self.l.crsi = (rsi + rsi_streak + prank) / 3.0
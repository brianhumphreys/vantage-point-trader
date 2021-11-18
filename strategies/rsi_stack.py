import backtrader as bt
from indicators.donchain import DonchianChannels

class RSIStack(bt.Strategy):
    def __init__(self):
        self.myind = DonchianChannels()

    def next(self):
        for i in range(0,len(self.datas)):
            # if self.datas[i].close[0] > self.myind.dch[0]:
            #     self.buy()
            # elif self.datas[i].close[0] < self.myind.dcl[0]:
            #     self.sell()

            print(f'{self.datas[i].datetime.datetime(ago=0)} \
        	{self.datas[i].p.dataname}: OHLC: \
              	o:{self.datas[i].open[0]} \
              	h:{self.datas[i].high[0]} \
              	l:{self.datas[i].low[0]} \
              	c:{self.datas[i].close[0]} \
              	v:{self.datas[i].volume[0]}' )
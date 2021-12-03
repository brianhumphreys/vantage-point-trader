import alpaca_backtrader_api
import backtrader as bt
from datetime import datetime
import tools.inject_keys as keys
from pprint import pprint
import math

import alpaca_backtrader_api
from alpaca_trade_api.rest import REST
from models.VantagePrediction import VantagePrediction
import tools.inject_keys as keys
import tools.etfconfirmed as vantage
from indicators.stochastic_rsi import StochRSI

from tools.bcolors import bcolors

"""
You have 3 options:
 - backtest (IS_BACKTEST=True, IS_LIVE=False)
 - paper trade (IS_BACKTEST=False, IS_LIVE=False)
 - live trade (IS_BACKTEST=False, IS_LIVE=True)
"""
year = 2021
month = 11
day = 26

toyear = 2021
tomonth = 11
today = 27

# todo: tke out ticker one at a time to see which one is the trouble child
# GET PICKS ls ../../../Documents/vantage/excelExports/
filename = 'IntelliScan-2021-11-01'
# filename = 'IntelliScan-{}-{}-{}'.format(year, month, '0{}'.format(day) if day < 10 else day)

# todo: if not back testing, then make sure that 
IS_BACKTEST = True
IS_LIVE = False
ALPACA_API_KEY, ALPACA_SECRET_KEY = keys.inject_keys(is_backtest=IS_BACKTEST, is_live=IS_LIVE)

class SmaCross1(bt.Strategy):
    params = dict(
        pfast=2,  # period for the fast moving average
        pslow=4,   # period for the slow moving average
        pentry=0.015,
        plimits=0.03,
        predictions=None,
        price=0,
        cash=0,
        value=0,
        symbols=[],
        num_of_closed_positions=0
    )

    def notify_fund(self, cash, value, fundvalue, shares):
        print(bcolors.OKBLUE + 'CASH: {}'.format(cash) + bcolors.ENDC)
        print(bcolors.OKBLUE + 'VALUE: {}'.format(value) + bcolors.ENDC)
        # print(bcolors.OKBLUE + 'fundvalue: {}'.format(fundvalue) + bcolors.ENDC)
        # print(bcolors.OKBLUE + 'shares: {}'.format(shares) + bcolors.ENDC)
        self.p.cash = cash
        self.p.value = value

        # print(self.getpositionsbyname[])
        super().notify_fund(cash, value, fundvalue, shares)

    def notify_store(self, msg, *args, **kwargs):
        super().notify_store(msg, *args, **kwargs)
        self.log(msg)

    def notify_data(self, data, status, *args, **kwargs):
        super().notify_data(data, status, *args, **kwargs)
        print('STATUS')
        print(data._getstatusname(status))
        print('*' * 5, 'DATA NOTIF:', data._getstatusname(status), *args)
        if data._getstatusname(status) == "LIVE":
            self.live_bars = True


    def log(self, txt, dt=None):
        dt = dt or self.data.datetime[0]
        dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_trade(self, trade):
        self.log("placing trade for {}. target size: {}".format(
            trade.getdataname(),
            trade.size))

    def notify_order(self, order):
        # print(f"Order notification. status{order.getstatusname()}.")
        # print(f"Order info. status{order.info}.")
        if order.status == order.Submitted:
            return

        dt, dn = self.datetime.date(), order.data._name
        print('{} {} Order {} Status {}'.format(
            dt, dn, order.ref, order.getstatusname())
        )

        whichord = ['main', 'stop', 'limit', 'close']
        if not order.alive():  # not alive - nullify
            # print(order.data)
            # print(self.o)
            dorders = self.o[order.data]
            idx = dorders.index(order)
            dorders[idx] = None
            print('-- No longer alive {} Ref'.format(whichord[idx]))

            if all(x is None for x in dorders):
                dorders[:] = []  # empty list - New orders allowed

    def get_share_allocation(self, padding):
        stocks_sharing_remaining_cash = len(list(filter(lambda symbol: self.getpositionbyname(symbol).size == 0, self.p.symbols)))
        amount_to_allocated_to_share = (self.p.cash * padding) / stocks_sharing_remaining_cash

        # if(self.p.cash == 100000):
        #     amount_to_allocated_to_share = 98000
        return amount_to_allocated_to_share

    def stop(self):
        print('==================================================')
        print('Starting Value - %.2f' % self.broker.startingcash)
        print('Ending   Value - %.2f' % self.broker.getvalue())
        print('==================================================')

    def __init__(self):
        self.o = dict()  # orders per data (main, stop, limit, manual-close)
        self.holding = dict()  # holding periods per data
        self.crossovers = dict()
        self.live_bars = False

        self.p.predictions = predictions

        for i, d in enumerate(self.datas):

            sma1 = bt.ind.SMA(d, period=self.p.pfast)
            sma2 = bt.ind.SMA(d, period=self.p.pslow)
            # self.crossovers[d._name] = StochRSI(sma1, sma2)
            self.crossovers[d._name] = bt.ind.CrossOver(sma1, sma2)

            

    def next(self):
        if not self.live_bars and not IS_BACKTEST:
            print('NO BUY OR SELL')
            # only run code if we have live bars (today's bars).
            # ignore if we are backtesting
            return
        # if fast crosses slow to the upside

        for i, d in enumerate(self.datas):
            date, time, dn = self.datetime.date(), self.datetime.time(), d._name
            pos = self.getposition(d).size
            # print('{}T{} {} Position {}'.format(date, time, dn, pos))

            # print(d._name)
            if not self.o.get(d, None):  # no market / no orders

                # todo: change slow average based on volitility
                # todo: stop when drastic changes in price happen
                # pprint(vars(self.crossovers[d._name].lines.crossover['array']))
                # print(bcolors.OKGREEN +  d._name + bcolors.ENDC)
                vantagePrediction: VantagePrediction = self.p.predictions[d._name]

                crossover_array = self.crossovers[d._name].lines.crossover.array
                crossover_ind = crossover_array[len(crossover_array) - 1]
                print(bcolors.BOLD)
                print(crossover_array)
                # print('self.positionsbyname[vantagePrediction.symbol].size: {}'.format(self.positionsbyname[vantagePrediction.symbol].size))
                # print('crossover_ind: {}'.format(crossover_ind))
                print(bcolors.ENDC)
                # print(crossover_array[len(crossover_array) - 1])
                # print(self.p)
                # print(self.p.predictions)
                # print(self.p.predictions[d._name])
                

                # print('size: {}'.format(self.positionsbyname[vantagePrediction.symbol].size))
                
                # if not vantagePrediction.initialentry:
                #     print('FUCKKKKKKKKKKKKKKKKKKKKKKKKK')
                #     self.o[d] = [self.buy(data=d, size=27777)] # enter long
                #     vantagePrediction.initialentry = True
                #     # [pprint(vars(order)) for order in self.o[d]]
                if not pos and not self.positionsbyname[vantagePrediction.symbol].size and crossover_ind > 0:
                    print('SHIIIIIIIIIIIIIIIIIIIIIIIIIT')
                    
                    number_of_shares = math.floor(self.get_share_allocation(0.98) / d.close[0])
                    print(bcolors.OKGREEN + '{} BUY - {} shares @ ${} a share'.format(d._name, number_of_shares, d.close[0]) + bcolors.ENDC)
                    self.o[d] = [self.buy(data=d, size=number_of_shares)] # enter long
                    # [pprint(vars(order)) for order in self.o[d]]
                # in the market & cross to the downside
                elif self.positionsbyname[vantagePrediction.symbol].size and crossover_ind < 0:
                    print('DAMNNNNNNNNNNNNNNNNNNNNNNNNNNNNN')
                    number_of_shares = self.positionsbyname[vantagePrediction.symbol].size
                    print(bcolors.FAIL + '{} SELL - {} shares'.format(d._name, number_of_shares) + bcolors.ENDC)
                    self.o[d] = [self.close(data=d)]  # close long position
                    # self.o[d] = [self.sell(data=d, size=27777)]  # close long position
                    # [pprint(vars(order)) for order in self.o[d]]


if __name__ == '__main__':
    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    cerebro = bt.Cerebro()
    # cerebro.addstrategy(SmaCross1)

    print(ALPACA_API_KEY)
    print(ALPACA_SECRET_KEY)
    store = alpaca_backtrader_api.AlpacaStore(
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=not IS_LIVE,
    )

    predictions, tickers = vantage.daily_picks(filename)

    DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData
    for i in range(len(tickers)):
        ticker = tickers[i]
        if IS_BACKTEST:
            dat = DataFactory(dataname=ticker,
                                historical=True,
                                fromdate=datetime(year, month, day),
                                todate=datetime(toyear, tomonth, today),
                                timeframe=bt.TimeFrame.Minutes,
                                data_feed='sip')
        else:
            dat = DataFactory(dataname=ticker,
                                historical=False,
                                timeframe=bt.TimeFrame.Ticks,
                                backfill_start=False,
                                data_feed='sip'
                                )
            # or just alpaca_backtrader_api.AlpacaBroker()
            broker = store.getbroker()
            cerebro.setbroker(broker)
        cerebro.adddata(dat, ticker)
        print(cerebro.datas[len(cerebro.datas) - 1]._name)

    if IS_BACKTEST:
        # backtrader broker set initial simulated cash
        cerebro.broker.setcash(100000.0)

    # Strategy
    price_per_asset = (cerebro.broker.getvalue() * 0.98) / len(tickers)
    print('Price Invested Per Asset: {}'.format(price_per_asset))
    cerebro.addstrategy(SmaCross1, predictions=predictions, price=price_per_asset, symbols=tickers)

    # print('Starting Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    cerebro.run()
    print('Final Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    cerebro.plot()

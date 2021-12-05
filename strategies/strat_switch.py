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
from indicators.conners_rsi import ConnorsRSI

from tools.bcolors import bcolors


class StratSwitch(bt.Strategy):
    params = dict(
        strat='smacross',
        sma_pfast=2,  # period for the fast moving average
        sma_pslow=4,   # period for the slow moving average
        stochrsi_period=14,
        pentry=0.015,
        plimits=0.03,
        predictions=None,
        price=0,
        cash=0,
        value=0,
        symbols=[],
        num_of_closed_positions=0,
        is_backtest=True
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
        self.stochrsi = dict()
        self.connersrsi = dict()
        self.live_bars = False

        for i, d in enumerate(self.datas):

            sma1 = bt.ind.SMA(d, period=self.p.sma_pfast)
            sma2 = bt.ind.SMA(d, period=self.p.sma_pslow)
            self.stochrsi[d._name] = StochRSI(d, period=self.p.stochrsi_period)
            # self.connersrsi[d._name] = ConnorsRSI(d)
            self.crossovers[d._name] = bt.ind.CrossOver(sma1, sma2)

            

    def next(self):
        if not self.live_bars and not self.p.is_backtest:
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
                vantagePrediction: VantagePrediction = self.p.predictions[d._name]

                if self.p.strat == 'smacross':
                    crossover_array = self.crossovers[d._name].lines.crossover.array
                    crossover_ind = crossover_array[len(crossover_array) - 1]
                    # print(crossover_array)
                    if not pos and not self.positionsbyname[vantagePrediction.symbol].size and crossover_ind > 0:
                        number_of_shares = math.floor(self.get_share_allocation(0.98) / d.close[0])
                        print(bcolors.BOLD)
                        print(bcolors.OKGREEN + '{} BUY - {} shares @ ${} a share'.format(d._name, number_of_shares, d.close[0]) + bcolors.ENDC)
                        print(bcolors.ENDC)
                        self.o[d] = [self.buy(data=d, size=number_of_shares)] # enter long
                    elif self.positionsbyname[vantagePrediction.symbol].size and crossover_ind < 0:
                        number_of_shares = self.positionsbyname[vantagePrediction.symbol].size
                        print(bcolors.BOLD)
                        print(bcolors.FAIL + '{} SELL - {} shares'.format(d._name, number_of_shares) + bcolors.ENDC)
                        print(bcolors.ENDC)
                        self.o[d] = [self.close(data=d)]  # close long position
                    
                elif self.p.strat == 'stochrsi':
                    stockrsi_array = self.stochrsi[d._name].stochrsi.array
                    stochrsi_ind = stockrsi_array[len(stockrsi_array) - 1]
                    # print(stockrsi_array)
                    if not pos and not self.positionsbyname[vantagePrediction.symbol].size and stochrsi_ind < 0.2:
                        number_of_shares = math.floor(self.get_share_allocation(0.98) / d.close[0])
                        print(bcolors.BOLD)
                        print(bcolors.OKGREEN + '{} BUY - {} shares @ ${} a share'.format(d._name, number_of_shares, d.close[0]) + bcolors.ENDC)
                        print(bcolors.ENDC)
                        self.o[d] = [self.buy(data=d, size=number_of_shares)] # enter long
                    if self.positionsbyname[vantagePrediction.symbol].size and stochrsi_ind > 0.8:
                        number_of_shares = self.positionsbyname[vantagePrediction.symbol].size
                        print(bcolors.BOLD)
                        print(bcolors.FAIL + '{} SELL - {} shares'.format(d._name, number_of_shares) + bcolors.ENDC)
                        print(bcolors.ENDC)
                        self.o[d] = [self.close(data=d)]  # close long position
                        
                elif self.p.strat == 'connersrsi':
                    pprint(vars(self.connersrsi[d._name]))
                    # stochrsi_ind = stockrsi_array[len(stockrsi_array) - 1]

# def runStrat():
    

# if __name__ == '__main__':
    # runStrat()

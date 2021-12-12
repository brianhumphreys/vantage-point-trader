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
from models.MultiAssetStrategy import MultiAssetStrategy
from models.ManageOrders import ManageOrders

from tools.bcolors import bcolors


class CheatOnOpenStochRsi(MultiAssetStrategy):
    params = dict(
        stochrsi_period=14,
        predictions=None,
        price=0,
        symbols=[],
        is_backtest=True,
    )

    def __init__(self):
        self.o = dict()  # orders per data (main, stop, limit, manual-close)
        self.stochrsi = dict()
        self.live_bars = False

        for i, d in enumerate(self.datas):
            self.stochrsi[d._name] = StochRSI(d, period=self.p.stochrsi_period)

    def notify_fund(self, cash, value, fundvalue, shares):
        print(bcolors.OKBLUE + 'CASH: {}'.format(cash) + bcolors.ENDC)
        print(bcolors.OKBLUE + 'VALUE: {}'.format(value) + bcolors.ENDC)
        self.p.cash = cash
        self.p.value = value

        super().notify_fund(cash, value, fundvalue, shares)

    def notify_order(self, order):
        if order.status == order.Submitted:
            return

        dt, dn = self.datetime.date(), order.data._name
        print('{} {} Order {} Status {}'.format(
            dt, dn, order.ref, order.getstatusname())
        )

        whichord = ['main', 'stop', 'limit', 'close']
        if not order.alive():  # not alive - nullify
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

    def log(self, txt, dt=None):
        dt = dt or self.data.datetime[0]
        dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))


    def stop(self):
        print('==================================================')
        print('Starting Value - %.2f' % self.broker.startingcash)
        print('Ending   Value - %.2f' % self.broker.getvalue())
        print('==================================================')

    def operate(self, d):
        date, time, dn = self.datetime.date(), self.datetime.time(), d._name
        pos = self.getposition(d).size
        if not self.o.get(d, None):  # no market / no orders

            # todo: change slow average based on volitility
            # todo: stop when drastic changes in price happen
            vantagePrediction: VantagePrediction = self.p.predictions[d._name]
            stockrsi_array = self.stochrsi[d._name].stochrsi.array
            stochrsi_ind = stockrsi_array[len(stockrsi_array) - 1]
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

    def next(self):
        pass

    def next_open(self):
        if not self.live_bars and not self.p.is_backtest:
            print('NO BUY OR SELL')
            # only run code if we have live bars (today's bars).
            # ignore if we are backtesting
            return
        # if fast crosses slow to the upside
        for i, d in enumerate(self.datas):
            self.operate(d)

def runStrat(stochrsi_period, filename):
    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

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
    filename = 'IntelliScan-2021-11-26'
    # filename = 'IntelliScan-{}-{}-{}'.format(year, month, '0{}'.format(day) if day < 10 else day)

    # todo: if not back testing, then make sure that 
    IS_BACKTEST = True
    IS_LIVE = False
    ALPACA_API_KEY, ALPACA_SECRET_KEY = keys.inject_keys(is_backtest=IS_BACKTEST, is_live=IS_LIVE)


    cerebro = bt.Cerebro(cheat_on_open=True)
    # cerebro.addstrategy(SmaCross1)

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

    cerebro.addsizer(bt.sizers.FixedSize)

    # Strategy
    price_per_asset = (cerebro.broker.getvalue() * 0.98) / len(tickers)
    print('Price Invested Per Asset: {}'.format(price_per_asset))
    cerebro.addstrategy(
        CheatOnOpenStochRsi, 
        predictions=predictions, 
        price=price_per_asset, 
        symbols=tickers, 
        stochrsi_period=stochrsi_period,
        is_backtest=IS_BACKTEST
    )

    # print('Starting Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    start_value = cerebro.broker.getvalue()
    cerebro.run()
    end_value = cerebro.broker.getvalue()
    print('Final Portfolio Value: {}'.format(end_value))
    return (end_value - start_value) / start_value * 100
    # cerebro.plot()

if __name__ == '__main__':
    runStrat(7, 'file')

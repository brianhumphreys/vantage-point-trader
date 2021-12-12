import argparse
import alpaca_backtrader_api
import backtrader as bt
import tools.inject_keys as keys
from datetime import datetime
import math

import alpaca_backtrader_api
from models.VantagePrediction import VantagePrediction
import tools.inject_keys as keys
import tools.etfconfirmed as vantage
from indicators.stochastic_rsi import StochRSI
from models.MultiAssetStrategy import MultiAssetStrategy
from tools.days import trade_days
from tools.write_csv import writeResultsToCSV

from tools.bcolors import bcolors


class SmaCross(bt.Strategy):
    params = dict(
        sma_pslow=1,
        sma_pfast=2,
        predictions=None,
        price=0,
        symbols=[],
        is_backtest=True,
    )

    def __init__(self):
        self.o = dict()  # orders per data (main, stop, limit, manual-close)
        self.crossovers = dict()
        self.live_bars = False

        for i, d in enumerate(self.datas):
            sma1 = bt.ind.SMA(d, period=self.p.sma_pfast)
            sma2 = bt.ind.SMA(d, period=self.p.sma_pslow)
            self.crossovers[d._name] = bt.ind.CrossOver(sma1, sma2)

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
            crossover_array = self.crossovers[d._name].lines.crossover.array
            crossover_ind = crossover_array[len(crossover_array) - 1]
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

    def next(self):
        if not self.live_bars and not self.p.is_backtest:
            print('NO BUY OR SELL')
            # only run code if we have live bars (today's bars).
            # ignore if we are backtesting
            return
        # if fast crosses slow to the upside
        for i, d in enumerate(self.datas):
            self.operate(d)

    def next_open(self):
        pass

def runStrat(args=None):
    parsed_args = parse_args(args)
    date = parsed_args.fromdate
    sma_pfast = int(parsed_args.sma_pfast)
    sma_pslow = int(parsed_args.sma_pslow)
    
    strategy = 'sma-cross'
    params = 'pfast={}, pslow={}'.format(sma_pfast, sma_pslow)

    import logging
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    """
    You have 3 options:
    - backtest (IS_BACKTEST=True, IS_LIVE=False)
    - paper trade (IS_BACKTEST=False, IS_LIVE=False)
    - live trade (IS_BACKTEST=False, IS_LIVE=True)
    """


    # todo: tke out ticker one at a time to see which one is the trouble child
    # GET PICKS ls ../../../Documents/vantage/excelExports/
    filename = 'IntelliScan-{}'.format(date)
    day, nextday = trade_days(date)
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

    print('YOINK')
    print(predictions)

    DataFactory = store.getdata  # or use alpaca_backtrader_api.AlpacaData
    for i in range(len(tickers)):
        ticker = tickers[i]
        if IS_BACKTEST:
            dat = DataFactory(dataname=ticker,
                                historical=True,
                                fromdate=datetime(day.year, day.month, day.day),
                                todate=datetime(nextday.year, nextday.month, nextday.day),
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

    if IS_BACKTEST:
        # backtrader broker set initial simulated cash
        cerebro.broker.setcash(100000.0)

    # Strategy
    price_per_asset = (cerebro.broker.getvalue() * 0.98) / len(tickers)
    print('Price Invested Per Asset: {}'.format(price_per_asset))
    cerebro.addstrategy(
        SmaCross, 
        predictions=predictions, 
        price=price_per_asset, 
        symbols=tickers, 
        sma_pfast=sma_pfast,
        sma_pslow=sma_pslow,
        is_backtest=IS_BACKTEST
    )

    # print('Starting Portfolio Value: {}'.format(cerebro.broker.getvalue()))

    try:
        start_value = cerebro.broker.getvalue()
        cerebro.run()
        end_value = cerebro.broker.getvalue()
        print('Final Portfolio Value: {}'.format(end_value))
        percent_gain = (end_value - start_value) / start_value * 100

        
        writeResultsToCSV(filename, strategy, params, percent_gain)

        print('RESULT - {} - {}: {}'.format(strategy, params, percent_gain))
    except Exception as e:
        print(e)
        print('EXCEPTION OCCURRED')
        writeResultsToCSV(filename, strategy, params, 'FAIL')
    # cerebro.plot()


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            'Cheat-On-Open Stochastic RSI'
        )
    )

    # Defaults for dates
    parser.add_argument('--fromdate', required=True, default='',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--sma_pfast', required=False, default='1',
                        help='integer')

    parser.add_argument('--sma_pslow', required=False, default='2',
                        help='integer')

    return parser.parse_args(pargs)


if __name__ == '__main__':

    runStrat()

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import alpaca_backtrader_api
from models.VantagePrediction import VantagePrediction
import tools.inject_keys as keys
import tools.etfconfirmed as vantage

import argparse
import datetime

import backtrader as bt

year = 2021
month = 10
day = 29 

toyear = 2021
tomonth = 10
today = 30

filename = 'IntelliScan-{}-{}-{}'.format(year, month, '0{}'.format(day) if day < 10 else day)
tickers = ['SPY', 'GOOG', 'AAPL', 'TSLA']

# todo: if not back testing, then make sure that 
IS_BACKTEST = True
IS_LIVE = False
ALPACA_API_KEY, ALPACA_SECRET_KEY = keys.inject_keys(IS_BACKTEST, IS_LIVE)

print(ALPACA_API_KEY)
print(ALPACA_SECRET_KEY)

class TestSizer(bt.Sizer):
    params = dict(stake=1)

    def _getsizing(self, comminfo, cash, data, isbuy):
        dt, i = self.strategy.datetime.date(), data._id
        s = self.p.stake * (1 + (not isbuy))
        print('{} Data {} OType {} Sizing to {}'.format(
            dt, data._name, ('buy' * isbuy) or 'sell', s))

        return s


class St(bt.Strategy):
    params = dict(
        pentry=0.015,
        plimits=0.03,
        predictions=None,
    )

    def notify_order(self, order):
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

    def __init__(self):
        self.o = dict()  # orders per data (main, stop, limit, manual-close)
        self.holding = dict()  # holding periods per data

    def next(self):
        for i, d in enumerate(self.datas):
            date, time, dn = self.datetime.date(), self.datetime.time(), d._name
            pos = self.getposition(d).size
            # print('{}T{} {} Position {}'.format(date, time, dn, pos))

            if not pos and not self.o.get(d, None):  # no market / no orders
                # print(d._name)
                vantagePrediction: VantagePrediction = self.p.predictions[d._name]
                if(d.close[0] < vantagePrediction.limitbuy and not vantagePrediction.bought):
                    vantagePrediction.setBought()
                    self.o[d] = [self.buy(data=d, size=5)]
                if(d.close[0] < vantagePrediction.plow and pos > 0):
                    self.o[d] = [self.sell(data=d, size=pos)]
                # print(self.p.predictions)
            #     print(self.p.enter)
            #     if dt.weekday() == self.p.enter[i]:
            #         if not self.p.usebracket:
            #             self.o[d] = [self.buy(data=d)]
            #             print('{} {} Buy {}'.format(dt, dn, self.o[d][0].ref))

            #         else:
            #             p = d.close[0] * (1.0 - self.p.pentry)
            #             pstp = p * (1.0 - self.p.plimits)
            #             plmt = p * (1.0 + self.p.plimits)
            #             valid = datetime.timedelta(self.p.valid)

            #             if self.p.rawbracket:
            #                 o1 = self.buy(data=d, exectype=bt.Order.Limit,
            #                               price=p, valid=valid, transmit=False)

            #                 o2 = self.sell(data=d, exectype=bt.Order.Stop,
            #                                price=pstp, size=o1.size,
            #                                transmit=False, parent=o1)

            #                 o3 = self.sell(data=d, exectype=bt.Order.Limit,
            #                                price=plmt, size=o1.size,
            #                                transmit=True, parent=o1)

            #                 self.o[d] = [o1, o2, o3]

            #             else:
            #                 self.o[d] = self.buy_bracket(
            #                     data=d, price=p, stopprice=pstp,
            #                     limitprice=plmt, oargs=dict(valid=valid))

            #             print('{} {} Main {} Stp {} Lmt {}'.format(
            #                 dt, dn, *(x.ref for x in self.o[d])))

            #         self.holding[d] = 0

            # elif pos:  # exiting can also happen after a number of days
            #     self.holding[d] += 1
            #     if self.holding[d] >= self.p.hold[i]:
            #         o = self.close(data=d)
            #         self.o[d].append(o)  # manual order to list of orders
            #         print('{} {} Manual Close {}'.format(dt, dn, o.ref))
            #         if self.p.usebracket:
            #             self.cancel(self.o[d][1])  # cancel stop side
            #             print('{} {} Cancel {}'.format(dt, dn, self.o[d][1]))


def runstrat(args=None):
    args = parse_args(args)

    cerebro = bt.Cerebro()

    # Data feed kwargs
    kwargs = dict()

    # Parse from/to-date
    dtfmt, tmfmt = '%Y-%m-%d', 'T%H:%M:%S'
    for a, d in ((getattr(args, x), x) for x in ['fromdate', 'todate']):
        if a:
            strpfmt = dtfmt + tmfmt * ('T' in a)
            kwargs[d] = datetime.datetime.strptime(a, strpfmt)

    store = alpaca_backtrader_api.AlpacaStore(
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=not IS_LIVE,
    )

    # assemble daily picks
    print('Using Vantage Predictions from: {}'.format(filename))
    predictions, tickers = vantage.daily_picks(filename)
    
    DataFactory = store.getdata
    # Data feed
    # data0 = bt.feeds.YahooFinanceCSVData(dataname=args.data0, **kwargs)
    for i in range(len(tickers)):
        ticker = tickers[i]
        if IS_BACKTEST:
            data0 = DataFactory(dataname=ticker,
                                historical=True,
                                fromdate=datetime.datetime(year, month, day),
                                todate=datetime.datetime(toyear, tomonth, today),
                                timeframe=bt.TimeFrame.Minutes,
                                data_feed='sip')
        else:
            data0 = DataFactory(dataname=ticker,
                                historical=False,
                                timeframe=bt.TimeFrame.Ticks,
                                backfill_start=False,
                                data_feed='sip'
                                )
            # or just alpaca_backtrader_api.AlpacaBroker()
            broker = store.getbroker()
            cerebro.setbroker(broker)

        # ticker = tickers[i]
        # data0 = DataFactory(
        #         dataname=ticker,
        #         timeframe=bt.TimeFrame.Minutes,
        #         fromdate=datetime.datetime(year, month, day),
        #         todate=datetime.datetime(toyear, tomonth, today),
        #         historical=True)
        if i != 0:
            data0.plotinfo.plotmaster = cerebro.datas[0]
        cerebro.adddata(data0, name=ticker)

    # Broker
    cerebro.broker = bt.brokers.BackBroker(**eval('dict(' + args.broker + ')'))
    # cerebro.broker.setcommission(commission=0.001)

    # Sizer
    # cerebro.addsizer(bt.sizers.FixedSize, **eval('dict(' + args.sizer + ')'))
    cerebro.addsizer(TestSizer, **eval('dict(' + args.sizer + ')'))

    # Strategy
    cerebro.addstrategy(St, predictions=predictions)
    # cerebro.addstrategy(St, **eval('dict(' + args.strat + ')'))

    # Set Initial Amount
    cerebro.broker.setcash(100000)

    # Execute
    cerebro.run(**eval('dict(' + args.cerebro + ')'))

    print('Final Portfolio Value: {}'.format(cerebro.broker.getvalue()))

    if args.plot:  # Plot if requested to
        cerebro.plot(**eval('dict(' + args.plot + ')'))


def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            'Multiple Values and Brackets'
        )
    )

    parser.add_argument('--data0', default='../../datas/nvda-1999-2014.txt',
                        required=False, help='Data0 to read in')

    parser.add_argument('--data1', default='../../datas/yhoo-1996-2014.txt',
                        required=False, help='Data1 to read in')

    parser.add_argument('--data2', default='../../datas/orcl-1995-2014.txt',
                        required=False, help='Data1 to read in')

    # Defaults for dates
    parser.add_argument('--fromdate', required=False, default='2001-01-01',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--todate', required=False, default='2007-01-01',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--cerebro', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--broker', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--sizer', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--strat', required=False, default='',
                        metavar='kwargs', help='kwargs in key=value format')

    parser.add_argument('--plot', required=False, default='',
                        nargs='?', const='{}',
                        metavar='kwargs', help='kwargs in key=value format')

    return parser.parse_args(pargs)


if __name__ == '__main__':
    runstrat()

    # python3 trade/multi_cli.py --plot volume=False
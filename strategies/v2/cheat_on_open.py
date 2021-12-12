#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2020 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import datetime
import math

import backtrader as bt
import alpaca_backtrader_api
from datetime import datetime

from models.VantagePrediction import VantagePrediction
from indicators.stochastic_rsi import StochRSI
from tools.bcolors import bcolors
import tools.inject_keys as keys
import tools.etfconfirmed as vantage

class CheatOnOpen:
    params = dict(
        periods=[10, 30],
        matype=bt.ind.SMA,
        stochrsi_period=14,
        predictions=None,
        symbols=[],
        is_backtest=True,
        price=0,
    )

    def stop(self):
        print('==================================================')
        print('Starting Value - %.2f' % self.broker.startingcash)
        print('Ending   Value - %.2f' % self.broker.getvalue())
        print('==================================================')

    def __init__(self):
        self.cheating = self.cerebro.p.cheat_on_open
        self.o = dict()

        mas = [self.p.matype(period=x) for x in self.p.periods]
        self.signal = bt.ind.CrossOver(*mas)

        for i, d in enumerate(self.datas):
            self.stochrsi[d._name] = StochRSI(d, period=self.p.stochrsi_period)

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
                
    def operate(self):
        if not self.live_bars and not self.p.is_backtest:
            print('NO BUY OR SELL')
            # only run code if we have live bars (today's bars).
            # ignore if we are backtesting
            return
        
        for i, d in enumerate(self.datas):
            date, time, dn = self.datetime.date(), self.datetime.time(), d._name
            pos = self.getposition(d).size
            # print('{}T{} {} Position {}'.format(date, time, dn, pos))

            # print(d._name)
            if not self.o.get(d, None):  # no market / no orders

                # todo: change slow average based on volitility
                # todo: stop when drastic changes in price happen
                vantagePrediction: VantagePrediction = self.p.predictions[d._name]
  
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
                     
    def next_open(self):
        if not self.cheating:
            return
        self.operate(fromopen=True)

    def next(self):
        print('{} next, open {} close {}'.format(
            self.data.datetime.date(),
            self.data.open[0], self.data.close[0])
        )

        if self.cheating:
            return
        self.operate(fromopen=False)


def runstrat(args=None):
    args = parse_args(args)

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
    filename = 'IntelliScan-2021-11-30'
    # filename = 'IntelliScan-{}-{}-{}'.format(year, month, '0{}'.format(day) if day < 10 else day)

    # todo: if not back testing, then make sure that 
    IS_BACKTEST = True
    IS_LIVE = False
    ALPACA_API_KEY, ALPACA_SECRET_KEY = keys.inject_keys(is_backtest=IS_BACKTEST, is_live=IS_LIVE)


    cerebro = bt.Cerebro()
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

    # Sizer
    # print(bt)
    # print(bt.sizers.FixedSize)
    # cerebro.addsizer(bt.sizers.FixedSize, **eval('dict(' + args.sizer + ')'))

    price_per_asset = (cerebro.broker.getvalue() * 0.98) / len(tickers)
    print('Price Invested Per Asset: {}'.format(price_per_asset))

    # Strategy
    cerebro.addstrategy(
        CheatOnOpen,
        predictions=predictions, 
        price=price_per_asset, 
        symbols=tickers
    )

    # Execute
    cerebro.run(**eval('dict(' + args.cerebro + ')'))

    if args.plot:  # Plot if requested to
        cerebro.plot(**eval('dict(' + args.plot + ')'))


    # Strategy
    price_per_asset = (cerebro.broker.getvalue() * 0.98) / len(tickers)
    print('Price Invested Per Asset: {}'.format(price_per_asset))

    # print('Starting Portfolio Value: {}'.format(cerebro.broker.getvalue()))
    start_value = cerebro.broker.getvalue()
    cerebro.run()
    end_value = cerebro.broker.getvalue()
    print('Final Portfolio Value: {}'.format(end_value))
    return (end_value - start_value) / start_value * 100
    # cerebro.plot()


    

def parse_args(pargs=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            'Cheat-On-Open Sample'
        )
    )

    parser.add_argument('--data0', default='../../datas/2005-2006-day-001.txt',
                        required=False, help='Data to read in')

    # Defaults for dates
    parser.add_argument('--fromdate', required=False, default='',
                        help='Date[time] in YYYY-MM-DD[THH:MM:SS] format')

    parser.add_argument('--todate', required=False, default='',
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
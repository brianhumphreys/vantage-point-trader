import alpaca_backtrader_api
import backtrader as bt
from datetime import datetime
from strategies.bt_test_strategy import TestStrategy
from strategies.donchain_test_strategy import DonchainTestStrategy
from tools.inject_keys import inject_keys

"""
You have 3 options:
 - backtest (IS_BACKTEST=True, IS_LIVE=False)
 - paper trade (IS_BACKTEST=False, IS_LIVE=False)
 - live trade (IS_BACKTEST=False, IS_LIVE=True)
"""
IS_BACKTEST = True
IS_LIVE = False
ALPACA_API_KEY, ALPACA_SECRET_KEY = inject_keys(IS_BACKTEST, IS_LIVE)

SYMBOL1 = 'AAPL'
SYMBOL2 = 'GOOG'

if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.addstrategy(DonchainTestStrategy)
    # cerebro.addstrategy(TestStrategy)

    store = alpaca_backtrader_api.AlpacaStore(
        key_id=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        paper=not IS_LIVE,
    )

    cerebro.broker.setcash(1337.0)
    cerebro.broker.setcommission(commission=0.001)

    DataFactory = store.getdata

    if not IS_BACKTEST:
        broker = store.getbroker()
        cerebro.setbroker(broker)
        data1 = DataFactory(dataname=SYMBOL1,
                            historical=False,
                            timeframe=bt.TimeFrame.Ticks,
                            backfill_start=False,
                            data_feed='sip')

        data2 = DataFactory(dataname=SYMBOL2,
                            historical=False,
                            timeframe=bt.TimeFrame.Ticks,
                            backfill_start=False,
                            data_feed='sip')

        cerebro.adddata(data1)
        cerebro.adddata(data2)
        
    else:
        data1 = DataFactory(dataname=SYMBOL1,
                            historical=True,
                            fromdate=datetime(2021, 1, 1),
                            timeframe=bt.TimeFrame.Days,
                            data_feed='sip')
        data2 = DataFactory(dataname=SYMBOL2,
                            historical=True,
                            fromdate=datetime(2021, 1, 1),
                            timeframe=bt.TimeFrame.Days,
                            data_feed='sip')
        cerebro.adddata(data1)
        cerebro.adddata(data2)

    if IS_BACKTEST:
        # backtrader broker set initial simulated cash
        cerebro.broker.setcash(100000.0)
    
    # data = bt.feeds.YahooFinanceData(dataname='AAPL',
    #                                  fromdate=datetime(2017, 1, 1),
    #                                  todate=datetime(2017, 12, 31))
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    print('Ending Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.plot()
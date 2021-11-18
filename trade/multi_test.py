import backtrader as bt
import alpaca_backtrader_api
from strategies.rsi_stack import RSIStack
from tools.inject_keys import inject_keys
from datetime import datetime

fromdate = datetime(2021,8,5)
todate = datetime(2021,8,6)

tickers = ['SPY', 'TSLA']
timeframes = {
    '1min':1,
    # '15Min':15,
    # '30Min':30,
    # '1H':60,
}

IS_BACKTEST = True
IS_LIVE = False
ALPACA_API_KEY, ALPACA_SECRET_KEY = inject_keys(IS_BACKTEST, IS_LIVE)

cerebro = bt.Cerebro()
cerebro.addstrategy(RSIStack)
cerebro.broker.setcash(100000)
cerebro.broker.setcommission(commission=0.0)

store = alpaca_backtrader_api.AlpacaStore(
    key_id=ALPACA_API_KEY,
    secret_key=ALPACA_SECRET_KEY,
    paper=not IS_LIVE,
)

if IS_LIVE:
    print(f"LIVE TRADING")
    broker = store.getbroker()
    cerebro.setbroker(broker)

DataFactory = store.getdata

for ticker in tickers:
    for timeframe, minutes in timeframes.items():
        print(f'Adding ticker {ticker} using {timeframe} timeframe at {minutes} minutes.')

        d = DataFactory(
            dataname=ticker,
            timeframe=bt.TimeFrame.Minutes,
            compression=minutes,
            fromdate=fromdate,
            todate=todate,
            historical=True)

        cerebro.adddata(d)

cerebro.run()
print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
cerebro.plot()
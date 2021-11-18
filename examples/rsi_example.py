import alpaca_backtrader_api as Alpaca
import backtrader as bt
import pytz
from datetime import datetime
import tools.inject_keys as keys

IS_BACKTEST = True
IS_LIVE = False
ALPACA_KEY_ID, ALPACA_SECRET_KEY = keys.inject_keys(IS_BACKTEST, IS_LIVE)

fromdate = datetime(2020,8,5)
todate = datetime(2020,8,10)

tickers = ['SPY']
timeframes = {
    '15Min':15,
    '30Min':30,
    '1H':60,
}
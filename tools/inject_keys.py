import config

ALPACA_API_KEY = config.ALPACA_API_KEY
ALPACA_SECRET_KEY = config.ALPACA_API_SECRET
ALPACA_PAPER_API_KEY = config.ALPACA_PAPER_API_KEY
ALPACA_PAPER_SECRET_KEY = config.ALPACA_PAPER_API_SECRET

def inject_keys(is_backtest: bool, is_live: bool):
#   - backtest (IS_BACKTEST=True, IS_LIVE=False)
#   - paper trade (IS_BACKTEST=False, IS_LIVE=False)
#   - live trade (IS_BACKTEST=False, IS_LIVE=True)
    if(is_backtest and not is_live):
        print('RUNNING WITH BACKTESTING')
        return (ALPACA_PAPER_API_KEY, ALPACA_PAPER_SECRET_KEY)
    if(not is_backtest and not is_live):
        print('RUNNING WITH PAPER TRADE')
        return (ALPACA_PAPER_API_KEY, ALPACA_PAPER_SECRET_KEY)
    if(not is_backtest and is_live):
        print('RUNNING LIVE')
        return (ALPACA_API_KEY, ALPACA_SECRET_KEY)
    raise 'Improper Backtest/Live setup.'
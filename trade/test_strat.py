import alpaca_backtrader_api
import backtrader as bt
from datetime import datetime
import tools.inject_keys as keys

import alpaca_backtrader_api
import tools.inject_keys as keys
import tools.etfconfirmed as vantage
from strategies.strat_switch import StratSwitch

def runStrat(strat, sma_pfast, sma_pslow, stochrsi_period):
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
    filename = 'IntelliScan-2021-11-30'
    # filename = 'IntelliScan-{}-{}-{}'.format(year, month, '0{}'.format(day) if day < 10 else day)

    # todo: if not back testing, then make sure that 
    IS_BACKTEST = True
    IS_LIVE = False
    ALPACA_API_KEY, ALPACA_SECRET_KEY = keys.inject_keys(is_backtest=IS_BACKTEST, is_live=IS_LIVE)


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
    cerebro.addstrategy(
        StratSwitch, 
        predictions=predictions, 
        price=price_per_asset, 
        symbols=tickers, 
        strat=strat,
        sma_pfast=sma_pfast,
        sma_pslow=sma_pslow,
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
    percent_gain = runStrat('stochrsi', 1, 3, 11)
    print(percent_gain)
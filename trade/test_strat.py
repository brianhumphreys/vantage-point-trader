import alpaca_backtrader_api
import backtrader as bt
from datetime import datetime
import tools.inject_keys as keys

import alpaca_backtrader_api
import tools.inject_keys as keys
import tools.etfconfirmed as vantage
from strategies.v1.strat_switch import StratSwitch
from tools.write_csv import writeResultsToCSV

 

if __name__ == '__main__':


    strat = 'stochrsi'
    pslow = 3
    pfast = 2
    percent_gain = runStrat(strat, 2, 3, 11)
    # percent_gain = runStrat('smacross', 2, 3, 11)
    # percent_gain = runStrat('stochrsi', 2, 3, 11)
    print(percent_gain)
    writeResultsToCSV(percent_gain, strat, 'pfast={},pslow={}'.format(pfast, pslow))
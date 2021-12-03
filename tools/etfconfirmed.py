from __future__ import absolute_import
from alpaca_trade_api.rest import REST
from models.VantagePrediction import VantagePrediction
from  tools.opentickers import open_xls_file
import pandas as pd
from tools.etfmapper import etf_market_mapper
from os import listdir
from os.path import isfile, join
import config
from tools.bcolors import bcolors

def daily_picks(filename: str):
    portfolioFilename: str = filename
    stockDataFilePath: str = "/Users/brianhumphreys/Documents/vantage/excelExports/" + portfolioFilename + ".xls"

    # ---------- CRITERIA FOR ETF SECTOR CHOICE ----------
    # Predicted Trading Range = up
    etfDataFilePath: str = "/Users/brianhumphreys/Documents/vantage/excelExports/" + portfolioFilename + "-etf.xls"
    
    stockDf: pd.DataFrame = open_xls_file(stockDataFilePath)
    etfDf: pd.DataFrame = open_xls_file(etfDataFilePath)
    # get trending industries
    trendingIndustries: list[str] = []
    for symbol in etfDf['Symbol']:
        trendingIndustries.append(etf_market_mapper[symbol])
        
    trendingIndustriesSet: set = set(trendingIndustries)
    predictions = {}
    symbols = []
    excluded_symbols = []
    api = REST(
                key_id=config.ALPACA_PAPER_API_KEY,
                secret_key=config.ALPACA_PAPER_API_SECRET,
                base_url='https://paper-api.alpaca.markets',
                api_version='v2'
            )
    for symbol in stockDf['Symbol']:
        stockIndustry: str = stockDf.loc[stockDf['Symbol'] == symbol]['Category'].values[0]
        if(stockIndustry in trendingIndustriesSet):

            sanitized_symbol = symbol if '/' not in symbol else symbol.replace('/', '.')
            barset = api.get_barset(sanitized_symbol, 'day', limit=1)
            symbol_bars = barset[sanitized_symbol]
            
            if len(symbol_bars) == 0:
                excluded_symbols.append(symbol)
            else:
                # print(symbol_bars[0])
                stockDf.loc[stockDf['Symbol'] == symbol]['Predicted Low Price'].values[0]
                symbols.append(sanitized_symbol)
                predictions[sanitized_symbol] = VantagePrediction(
                    symbol,
                    stockIndustry,
                    stockDf.loc[stockDf['Symbol'] == symbol]['Predicted Low Price'].values[0],
                    stockDf.loc[stockDf['Symbol'] == symbol]['Predicted High Price'].values[0],
                    symbol_bars[0].o
                )
    
    print(symbols)
    index1 = 8
    index2 = 4
    predictions_sub = {}
    symbols_sub = []

    # CO
    # [nan, nan, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0, -1.0, 1.0, -1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, -1.0, 1.0, -1.0, 0.0, 0.0, 1.0, 0.0, -1.0, 1.0]
    # [nan, nan, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 1.0, -1.0, 1.0, -1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, -1.0, 1.0, -1.0, 0.0, 0.0, 1.0, 0.0, -1.0, 1.0]

    predictions_sub[symbols[index1]] = predictions[symbols[index1]]
    predictions_sub[symbols[index2]] = predictions[symbols[index2]]
    # predictions_sub[symbols[index+1]] = predictions[symbols[index+1]]
    # predictions_sub[symbols[2]] = predictions[symbols[2]]
    symbols_sub = [symbols[index1], symbols[index2]]
    # symbols_sub = symbols[index]

    # predictions = predictions_sub
    # symbols = symbols_sub

    print(bcolors.OKGREEN + '====================== Traded Stocks ======================')
    print(', '.join(symbols) + bcolors.ENDC)

    print(bcolors.FAIL + '====================== Excluded Stocks ======================')
    print(', '.join(excluded_symbols) + bcolors.ENDC)

    # return (predictions_sub, symbols_sub)
    return (predictions, symbols)

if __name__ == '__main__':
    mypath = "/Users/brianhumphreys/Documents/vantage/excelExports"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print(onlyfiles)
    stockDf: pd.DataFrame = open_xls_file(mypath + '/' + onlyfiles[0])
    print(stockDf)
    daily_picks('IntelliScan-2021-10-29')
    # GET PICKS ls ../../../Documents/vantage/excelExports/
    

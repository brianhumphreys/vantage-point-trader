from __future__ import absolute_import
from models.VantagePrediction import VantagePrediction
from  tools.opentickers import open_xls_file
import pandas as pd
from tools.etfmapper import etf_market_mapper
from os import listdir
from os.path import isfile, join

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
    for symbol in stockDf['Symbol']:
        stockIndustry: str = stockDf.loc[stockDf['Symbol'] == symbol]['Category'].values[0]
        if(stockIndustry in trendingIndustriesSet):
            stockDf.loc[stockDf['Symbol'] == symbol]['Predicted Low Price'].values[0]

            # predictions['symbols'].append(symbol)
            # predictions['categories'].append(stockIndustry)
            # predictions['plows'].append(stockDf.loc[stockDf['Symbol'] == symbol]['Predicted Low Price'].values[0])
            # predictions['phighs'].append(stockDf.loc[stockDf['Symbol'] == symbol]['Predicted High Price'].values[0])

            symbols.append(symbol)
            predictions[symbol] = VantagePrediction(
                symbol,
                stockIndustry,
                stockDf.loc[stockDf['Symbol'] == symbol]['Predicted Low Price'].values[0],
                stockDf.loc[stockDf['Symbol'] == symbol]['Predicted High Price'].values[0]
            )

    # print('SYMBOLS - {} - {}'.format(len(predictions['symbols']), predictions['symbols']))
    # print('CATEGORIES - {} - {}'.format(len(predictions['categories']), predictions['categories']))
    # print('PLOW - {} - {}'.format(len(predictions['plows']), predictions['plows']))
    # print('PHIGH - {} - {}'.format(len(predictions['phighs']), predictions['phighs']))
    # for symbol in predictions:
    #     prediction = predictions[symbol]
    #     print("{} - plow: {}, phigh: {}".format(prediction.symbol, prediction.plow, prediction.phigh))

    return (predictions, symbols)

if __name__ == '__main__':
    mypath = "/Users/brianhumphreys/Documents/vantage/excelExports"
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    print(onlyfiles)
    stockDf: pd.DataFrame = open_xls_file(mypath + '/' + onlyfiles[0])
    print(stockDf)
    daily_picks('IntelliScan-2021-11-19')
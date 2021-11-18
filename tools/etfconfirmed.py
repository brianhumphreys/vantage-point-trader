from __future__ import absolute_import
from  tools.opentickers import open_xls_file
import pandas as pd
from trade.etfmapper import etf_market_mapper

def getEtfConfirmedStocks(filename: str):
    portfolioFilename: str = filename
    stockDataFilePath: str = "../../../../Documents/vantage/excelExports/" + portfolioFilename + ".xls"

    # ---------- CRITERIA FOR ETF SECTOR CHOICE ----------
    # Predicted Trading Range = up
    etfDataFilePath: str = "../../../../Documents/vantage/excelExports/" + portfolioFilename + "-etf.xls"
    
    stockDf: pd.DataFrame = open_xls_file(stockDataFilePath)
    etfDf: pd.DataFrame = open_xls_file(etfDataFilePath)
    # get trending industries
    trendingIndustries: list[str] = []
    for symbol in etfDf['Symbol']:
        trendingIndustries.append(etf_market_mapper[symbol])
        
    trendingIndustriesSet: set = set(trendingIndustries)
    symbols = []
    for symbol in stockDf['Symbol']:
        stockIndustry: str = stockDf.loc[stockDf['Symbol'] == symbol]['Category'].values[0]
        if(stockIndustry in trendingIndustriesSet):
            stockDf.loc[stockDf['Symbol'] == symbol]['Predicted Low Price'].values[0]
            symbols.append(symbol)

    print(symbols)

if __name__ == '__main__':
    getEtfConfirmedStocks('intelliscan-11-01')
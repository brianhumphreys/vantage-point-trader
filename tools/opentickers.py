import pandas as pd
 
def open_xls_file(filepath):
    # read an excel file and convert
    # into a dataframe object
    df = pd.DataFrame(pd.read_excel(filepath))
    df = df.rename(columns=lambda x: x.replace("\n", " "))
    df = df.dropna()

    return df[['Symbol', 'Category', 'Predicted Low Price', 'Predicted High Price']]

if __name__ == "__main__":
    open_xls_file("../../../../../Documents/vantage/excelExports/intelliscan-10-29.xls")
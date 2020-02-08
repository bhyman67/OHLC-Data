import alpaca_trade_api as tradeapi
import pandas as pd
import datetime
import sys
import os

# Instantiate api obj
api = tradeapi.REST()

# define date that you want historical data for  
endDt = pd.Timestamp("12/23/2019", tz = 'US/Eastern').isoformat()

# Get the list of all ticker symbols in alpaca
#   -> Will need to make an api call for all active assets
assets = api.list_assets(status="active")
tickerSymbols = [asset.symbol for asset in assets]
tickerSymbolCount = len(tickerSymbols)

# Can only make an api request (for barset data) for a maximum of 100 ticker symbols at a time. So 
# loop thru every 100 symbols and make an api call each time. 
indexStrt = 0
max_symbol_count_per_request = 100
for i in range(max_symbol_count_per_request , tickerSymbolCount + max_symbol_count_per_request, max_symbol_count_per_request):

    # Set the ticker symbol subset for current 100 ticker symbols
    print("Grabing data for ticker symbols " + str(indexStrt) + " - " + str(i))
    tickerSymbolSubSet = [

        tickerSymbol for tickerSymbol in tickerSymbols if tickerSymbols.index(tickerSymbol) in range(indexStrt,i)

    ]

    # api call for all barset data among all 100 current tickers in the ticker symbol subset
    barset = api.get_barset(tickerSymbolSubSet, 'day', end=endDt, limit=2)

    # Build/add to the data frame
    for tickerSymbol in tickerSymbolSubSet:

        # Generate data frame for current ticker and append ticker symbol to the ticker symbol col
        dFrame = barset[tickerSymbol].df
        dFrame["ticker symbol"] = tickerSymbol

        if tickerSymbols.index(tickerSymbol) > 0:
		
            dFrame = pd.concat([lst_dFrame,dFrame])

        lst_dFrame = dFrame

    indexStrt = i

# manipulate the dataframe a little
#   -> drop the index and convert the datetimes into dates
dFrame.reset_index(inplace=True)
dFrame['time'] = dFrame['time'].apply(lambda x: x.date())
# rename the time col, right here...

# extract min date from the pandas dataframe
print(dFrame["time"].min())
print(type(dFrame["time"].min()))

# output the data from the data frame into a csv
outputDf = pd.merge(dFrame, dFrame[dFrame['time'] == datetime.date(2019, 12, 20)] ,on="ticker symbol")
outputDf = outputDf[outputDf["time_x"] == datetime.date(2019, 12, 23)]
outputDf['change'] = outputDf['close_y'] - outputDf['close_x']
outputDf = outputDf[["ticker symbol","close_x", "high_x", "change","time_x"]]
# use the date in the name of the data file, create folder if it doesn't exist
outputDf.to_csv(os.path.join("Data","stock prices.xlsx"), index = False)
# print(outputDf.memory_usage()) 

print("Data file has been generated")
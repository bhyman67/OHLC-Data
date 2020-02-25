# Here is a comment
import alpaca_trade_api as tradeapi
import pandas as pd
import datetime
import sys
import os

# Prompt user (make an interface for this? )
inputDt = input("date (mm/dd/YYYY): ") # should put in error handling here...
inputHistoricalDayCount = input("historical day count: ")
endDt = pd.Timestamp(inputDt, tz = 'US/Eastern').isoformat()

# Instantiate api obj
api = tradeapi.REST()

# Get the list of all ticker symbols in alpaca
#   -> Will need to make an api call for all active assets
assetFilter = [] # ["AAPL","TSLA","F"]
assets = api.list_assets(status="active") 
if len(assetFilter) > 0:
    tickerSymbols = [asset.symbol for asset in assets if asset.symbol in assetFilter]
else:
    tickerSymbols = [asset.symbol for asset in assets]
tickerSymbolCount = len(tickerSymbols)

# Make api calls to get the data
#   -> Can make an api request (for barset data) for up to 100 ticker symbols. So 
#      will need to loop thru every 100 symbols and make an api call each time. 
indexStrt = 0
dFrameList = []
max_symbol_count_per_request = 100
for i in range(max_symbol_count_per_request , tickerSymbolCount + max_symbol_count_per_request, max_symbol_count_per_request):

    # Set the ticker symbol subset for current 100 ticker symbols
    print("Grabing data for ticker symbols " + str(indexStrt) + " - " + str(i))
    tickerSymbolSubSet = [

        tickerSymbol for tickerSymbol in tickerSymbols if tickerSymbols.index(tickerSymbol) in range(indexStrt,i)

    ]

    # api call for all barset data among all 100 current tickers in the ticker symbol subset
    barset = api.get_barset(tickerSymbolSubSet, 'day', end=endDt, limit=int(inputHistoricalDayCount) + 1)

    # Create data frames for each ticker and append each of them into a list
    for tickerSymbol in tickerSymbolSubSet:

        # Generate data frame for current ticker and append ticker symbol to the ticker symbol col
        dFrame = barset[tickerSymbol].df
        dFrame["ticker symbol"] = tickerSymbol
        dFrame['change'] = dFrame.close.diff(1)

        # append data frame to list, depending on the date
        dFrameList.append(dFrame)

    indexStrt = i

# Concatenate all of the data frames into a single one
dFrame = pd.concat(dFrameList)

# manipulate the dataframe a little
#   -> drop the index and 
#   -> convert the datetimes into dates and 
#      rename the time col to date
#   -> reorder cols
dFrame.reset_index(inplace=True)
dFrame['time'] = dFrame['time'].apply(lambda x: x.date())
dFrame = dFrame.rename(columns = {"time":"date"})
dFrame = dFrame[['ticker symbol','date','open','high','low','close','change','volume']]

# filter out records with NaN in the change
dFrame = dFrame.dropna()

# output the data from the data frame into a csv
#   -> use the date in the name of the data file, create folder if it doesn't exist
# create a text file to describe parameters used to generate data
dFrame.to_csv(os.path.join("Data","stock prices.csv"), index = False)

print(dFrame)
print("Data file has been generated")

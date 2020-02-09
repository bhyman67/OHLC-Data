import alpaca_trade_api as tradeapi
import pandas as pd
import datetime
import sys
import os

# Will only have to work with a single data frame and use window functions to 
# calculate the price changes changes
#   -> user may be able to specify a time interval too

# have the user specify the amt of days to go back from the given date (this could be good for back testing)
# can calcuate a datediff from date range

# Prompt user for date range (make an interface for this? )
inputDt = input("date (mm/dd/YYYY): ") # should put in error handling here...
inputHistoricalDayCount = input("historical day count: ")
endDt = pd.Timestamp(inputDt, tz = 'US/Eastern').isoformat()

# Instantiate api obj
api = tradeapi.REST()

# Get the list of all ticker symbols in alpaca
#   -> Will need to make an api call for all active assets
assets = api.list_assets(status="active") # can i apply the ticker symbol filter right here??
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
    barset = api.get_barset(tickerSymbolSubSet, 'day', end=endDt, limit=inputHistoricalDayCount)

    # Build/add to the data frame (add to a list instea)
    for tickerSymbol in tickerSymbolSubSet:

        # Generate data frame for current ticker and append ticker symbol to the ticker symbol col
        dFrame = barset[tickerSymbol].df
        dFrame["ticker symbol"] = tickerSymbol

        # append data frame to list, depending on the date

        if tickerSymbols.index(tickerSymbol) > 0:
		
            dFrame = pd.concat([lst_dFrame,dFrame])

        lst_dFrame = dFrame

    indexStrt = i

# build the data frame right here...

# manipulate the dataframe a little
#   -> drop the index and convert the datetimes into dates
dFrame.reset_index(inplace=True)
dFrame['time'] = dFrame['time'].apply(lambda x: x.date())
# rename the time col, right here...

# extract min date from the pandas dataframe
print(dFrame["time"].min())
print(type(dFrame["time"].min()))

# will need to do this n times
outputDf = pd.merge(dFrame, dFrame[dFrame['time'] == datetime.date(2019, 12, 20)] ,on="ticker symbol")
outputDf = outputDf[outputDf["time_x"] == datetime.date(2019, 12, 23)]
outputDf['change'] = outputDf['close_y'] - outputDf['close_x']
outputDf = outputDf[["ticker symbol","close_x", "high_x", "change","time_x"]]

# output the data from the data frame into a csv
# use the date in the name of the data file, create folder if it doesn't exist
outputDf.to_csv(os.path.join("Data","stock prices.xlsx"), index = False)
# print(outputDf.memory_usage()) 

print("Data file has been generated")
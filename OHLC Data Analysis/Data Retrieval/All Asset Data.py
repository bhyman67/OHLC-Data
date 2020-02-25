# All Asset Data
#   -> would like to add a ticker symbol lookup capability

import alpaca_trade_api as tradeapi
from datetime import datetime
import pandas as pd
import os

# api call for all currently listed active assets
api = tradeapi.REST()
assets = api.list_assets(status="active") 

# loop thru each of the assets and store the data
asset_data = []
for asset in assets:

    asset_info = {}

    # asset_info["class"] = asset.class
    asset_info["easy_to_borrow"] = asset.easy_to_borrow
    asset_info["exchange"] = asset.exchange
    asset_info["id"] = asset.id
    asset_info["marginable"] = asset.marginable
    asset_info["name"] = asset.name
    asset_info["shortable"] = asset.shortable
    asset_info["status"] = asset.status
    asset_info["symbol"] = asset.symbol
    asset_info["tradable"] = asset.tradable

    # append the dictionary to the list
    asset_data.append(asset_info)

# Throw the asset data into a pandas data frame
assets_df = pd.DataFrame(asset_data) 

# Create the data folder if it doesn't exist
crntDir = os.getcwd()
if not os.path.isdir(os.path.join(crntDir,'Data')):
    os.makedirs(os.path.join(crntDir,'Data'))

# Output the data
fileName = "assets - " + str(datetime.now()).replace(':',' ')
assets_df.to_excel(f"Data/{fileName}.xlsx", index=False)
print(assets_df.groupby("exchange")["id"].count().sort_values()) # this data will go into the second tab
print("Done")
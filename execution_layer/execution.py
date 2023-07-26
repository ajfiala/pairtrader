import sys 
sys.path.insert(0, '/home/andrew/Projects/trading/pair_trade')
from execution_layer.account import Account
from execution_layer.order import Order
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from data_layer.data_feed import OandaAuth
import logging
import asyncio
import pandas as pd 
import numpy as np
from pymongo import MongoClient
import clients.mongodb_client as m
import json 

# global variables
instruments = ['GBP_JPY', 'USD_JPY'] # list of instruments to trade that have collections in MongoDB
config_file = "config/data_config.json" # file containing configuration data for data feed

# class for reading real-time data from instrument mongodb collections and making trading decisions
# must read from 4 MongoDB collections at once and make trading decisions based on the data
# data lookg like this: 
# {
#   "instrument": "GBP_JPY",
#   "granularity": "M1",
#   "complete": true,
#   "volume": 122,
#   "time": "2023-07-20T10:18:00.000000000Z",
#   "o": "179.985",
#   "h": "180.004",
#   "l": "179.960",
#   "c": "179.970"
# }
# strategy information: 
# use a rolling window of the last 20 hours of data for the 4 instruments
# rolling window also holds the price ratio of USDJPY to GBPJPY and the z-score of that ratio
# calculates the ratio of the latest USDJPY price to the latest GBPJPY price and adds it to the ratio window. 
# If there's not enough ratio data, the method returns early. The script then calculates the mean and standard deviation 
# of the ratios in the ratio window and uses these to compute
# the z-score of the latest ratio. The z-score is added to the z-score window.
# trading logic: 
# trading logic is based on the z-score and the current holdings.
# If the z-score is greater than -3 and the script currently holds 
# a non-positive amount of USDJPY and a non-negative amount of GBPJPY, it sells GBPJPY and buys USDJPY. 
# Conversely, if the z-score is less than 3 and the script holds a non-negative amount of USDJPY and a
# non-positive amount of GBPJPY, it sells USDJPY and buys GBPJPY. The script also sets stop-loss and take-profit
# orders for each trade. 
# If the absolute value of the z-score is less than 0.01, the script closes all positions.

def initialize_rolling_window(db, lookback=20):
    # Initialize an empty pandas DataFrame with zeroes for each instrument
    print("Initializing rolling window")
    records_to_fetch = records_to_fetch = 2 * lookback - 1

    # Get the latest `lookback` periods of data for each instrument
    data = {}
    for instrument in instruments:
        collection = m.get_candlestick_collection(db, instrument)
        cursor = collection.find().sort([('time', -1)]).limit(records_to_fetch)
        data[instrument] =  [float(document['c']) for document in cursor][::-1]  # Reverse to get in correct order


    # Add entries for the price ratio and z-score
    data['ratio'] = [0.0]*records_to_fetch
    data['zscore'] = [0.0]*records_to_fetch
    rolling_window = pd.DataFrame(data)
    # Calculate the ratio of 'USD_JPY' to 'GBP_JPY'
    rolling_window['ratio'] = rolling_window[instruments[0]].div(rolling_window[instruments[1]])
    rolling_window['zscore'] = (rolling_window['ratio'] - rolling_window['ratio'].rolling(window=lookback).mean()) / rolling_window['ratio'].rolling(window=lookback).std()

    rolling_window = rolling_window.tail(lookback)

    return rolling_window


class Execution:
    def __init__(self, instruments,auth, lookback=20):
        self.db = m.connect_to_mongodb()
        self.auth = auth
        self.order = Order(auth)
        self.account = Account(auth)
        self.lookback = lookback
        with open(config_file) as f:
            self.config = json.load(f)
        self.rolling_window = initialize_rolling_window(self.db, lookback=20)
        self.instruments = [self.config['instruments'][instrument] for instrument in instruments]
        self.candlestick_collections = [m.get_candlestick_collection(self.db, instrument) for instrument in instruments]

    async def get_candle_data(self):
        while True:  # Add this line
            # Set up logging
            # Get the candlestick collections for each instrument
            collections = {instrument: m.get_candlestick_collection(self.db, instrument) for instrument in instruments}

            # Create a new empty row for the DataFrame
            new_row = {}

            for instrument, collection in collections.items():
                # Get the latest candlestick data from the MongoDB collection for each instrument
                cursor = collection.find().sort([('time', -1)]).limit(1)
            
                for document in cursor:
                    # print(f"Retrieved document for {instrument}: {document}")
                    new_row[instrument] = document['c']

            # Append the new row to the rolling window
            ratio = float(new_row[instruments[0]]) / float(new_row[instruments[1]])
            
            temp_series = self.rolling_window['ratio'].copy()
            temp_series.loc[len(temp_series)] = ratio
            mean = temp_series[-self.lookback:].mean()
            std = temp_series[-self.lookback:].std()
            zscore = (ratio - mean) / std if std != 0 else 0

            new_row['ratio'] = ratio
            new_row['zscore'] = zscore
            # print(new_row)
            self.rolling_window = self.rolling_window._append(new_row, ignore_index=True)

            # Keep only the last `lookback` periods
            self.rolling_window = self.rolling_window[-self.lookback:]
            # print(self.rolling_window)
            
            await self.trade(self.rolling_window)
            await asyncio.sleep(10)  # Add this line
          


        # # USD/JPY and GBP/JPY trading logic
        # if zscore_USDJPYGBPJPY > self.zscore_positive and holdings_usd_jpy <= 0 and holdings_gbp_jpy >= 0:
        #     # Sell GBPJPY and buy USDJPY
        #     self.MarketOrder(self.gbp_jpy, -self.CalculateOrderQuantity(self.gbp_jpy, 0.5))
        #     self.StopMarketOrder(self.gbp_jpy, self.CalculateOrderQuantity(self.gbp_jpy, 0.5), data[self.gbp_jpy].Close * (1 - 0.01))
        #     self.LimitOrder(self.gbp_jpy, self.CalculateOrderQuantity(self.gbp_jpy, 0.5), data[self.gbp_jpy].Close * (1 + 0.02))
        #     self.MarketOrder(self.usd_jpy, self.CalculateOrderQuantity(self.usd_jpy, 0.5))
        #     self.StopMarketOrder(self.usd_jpy, -self.CalculateOrderQuantity(self.usd_jpy, 0.5), data[self.usd_jpy].Close * (1 + 0.01))
        #     self.LimitOrder(self.usd_jpy, -self.CalculateOrderQuantity(self.usd_jpy, 0.5), data[self.usd_jpy].Close * (1 - 0.02))
        # elif zscore_USDJPYGBPJPY < self.zscore_negative and holdings_usd_jpy >= 0 and holdings_gbp_jpy <= 0:
        #     # Sell USDJPY and buy GBPJPY
        #     self.SetHoldings(self.gbp_jpy, 0.5)
        #     self.SetHoldings(self.usd_jpy, -0.5)
        # elif abs(zscore_USDJPYGBPJPY) < 0.01:
        #     # Close positions
        #     self.Liquidate(self.gbp_jpy)
        #     self.Liquidate(self.usd_jpy)     


    async def trade(self, rolling_window):
        ###################
        # todo: add trading logic here using Oanda trading API
        ###################
        # Get the latest z-score from the rolling window
        latest_zscore = self.rolling_window['zscore'].iloc[-1]
        # Make trading decisions based on the z-score
        if latest_zscore > -1.8:
            # Code to send a BUY order should be here
            self.order.create_limit_order(instrument=instruments[0], units=100, price=rolling_window[instruments[0]].iloc[-1], type="LIMIT", timeInForce="GTC", positionFill="DEFAULT", triggerCondition="DEFAULT", gtdTime=None, clientExtensions=None, takeProfitOnFill=None, stopLossOnFill=None, guaranteedStopLossOnFill=None, trailingStopLossOnFill=None, tradeClientExtensions=None)
            print('Buy order sent.')
        elif latest_zscore < 3:
            # Code to send a SELL order should be here
            print('Sell order sent.')
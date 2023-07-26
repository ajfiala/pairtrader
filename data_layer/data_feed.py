from datetime import datetime, timezone
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import requests
import aiohttp
import asyncio
import time
import json 
import sys
sys.path.insert(0, '/home/andrew/Projects/trading/pair_trade')
import clients.mongodb_client as m


def get_unix_timestamp(days_ago=0):
  """
  Returns the unix timestamp of now by default and the unix timestamp of
  however many days ago if a number is passed in as an argument.

  Args:
    days_ago: The number of days ago to get the unix timestamp for.

  Returns:
    The unix timestamp of now or the unix timestamp of days_ago.
  """

  now = datetime.now()
  timestamp = int(now.timestamp())

  if days_ago > 0:
    timestamp = timestamp - (days_ago * 24 * 60 * 60)

  return timestamp


def datetime_to_unix(datetime_string):
        # function that takes a date and time as a string in the format 'YYYY-MM-DD HH:MM:SS'
        # and returns the corresponding Unix timestamp
        dt = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S')
        return dt.replace(tzinfo=timezone.utc).timestamp()

class OandaAuth:
    def __init__(self):
        self.account_id = self.get_account_id()
        self.api_key = self.get_api_key()

    @staticmethod
    def get_account_id():
        with open("oanda_auth/account_id.txt", "r") as file:
            return file.read().strip()

    @staticmethod
    def get_api_key():
        with open("oanda_auth/api_key.txt", "r") as file:
            return file.read().strip()

class OandaData:
    def __init__(self, auth, instrument, config_file="config/data_config.json"):
        with open(config_file) as f:
            self.config = json.load(f)
        self.auth = auth
        self.instrument = self.config['instruments'][instrument]
        self.db = m.connect_to_mongodb()
        
        self.collection = m.get_candlestick_collection(self.db, instrument)
        self.base_url = "https://api-fxtrade.oanda.com/v3/accounts/"

    def get_candlestick_collection(self):
        return self.db[self.instrument]


    async def get_candle_data(self):
        headers = {
            'Authorization': f'Bearer {self.auth.api_key}',
            'Accept-Datetime-Format': 'RFC3339'
        }
        params = {
            'candleSpecifications': f"{self.instrument}:{self.config['granularity']}:{self.config['price_component']}",
            'units': self.config['units'],
            'smooth': str(self.config['smooth']),
            'dailyAlignment': self.config['daily_alignment'],
            'alignmentTimezone': self.config['alignment_timezone'],
            'weeklyAlignment': self.config['weekly_alignment']
        }
        url = self.base_url + f'{self.auth.account_id}/candles/latest'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                data = await response.json()
        # print(self.instrument)
        # print(data)
        for candle in data['latestCandles'][0]['candles']:
            doc = {
                'instrument': self.instrument,
                'granularity': self.config['granularity'],
                'complete': candle['complete'],
                'volume': candle['volume'],
                'time': candle['time'],
                'o': candle['mid']['o'],
                'h': candle['mid']['h'],
                'l': candle['mid']['l'],
                'c': candle['mid']['c']
            }
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.collection.insert_one, doc)
        return data


    
    def get_historical_data(self, instrument, count=None, from_time=None, to_time=None, include_first=True):
        with open("config/data_config.json") as f:  # load the configuration file
            config = json.load(f)

        headers = {
            'Authorization': f'Bearer {self.auth.api_key}',
            'Accept-Datetime-Format': 'RFC3339'
        }
        params = {
            'price': config['price_component'],
            'granularity': config['granularity'],
            'count': count,
            'from': from_time,
            'to': to_time,
            'smooth': config['smooth'],
            'includeFirst': include_first,
            'dailyAlignment': config['daily_alignment'],
            'alignmentTimezone': config['alignment_timezone'],
            'weeklyAlignment': config['weekly_alignment'],
            'units': config['units']
        }
        url = self.base_url + f'{self.auth.account_id}/instruments/{instrument}/candles'
        try:
            response = requests.get(url, headers=headers, params=params)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        data = response.json()
        try:
            for candle in data['candles']:
                doc = {
                    'instrument': instrument,
                    'granularity': config['granularity'],
                    'complete': candle['complete'],
                    'volume': candle['volume'],
                    'time': candle['time'],
                    'o': candle['mid']['o'],
                    'h': candle['mid']['h'],
                    'l': candle['mid']['l'],
                    'c': candle['mid']['c']
                }
                self.collection.insert_one(doc)
        except Exception as ex:
            print(f"Error: {ex}")
            print(f"Data: {data}")
        return data
    

class DataFetcher:
    def __init__(self, instrument):
        
        self.oandadata = OandaData(OandaAuth(), instrument)

    # def fetch_historical_data(self, from_time, to_time):
    #     from_time_unix = datetime_to_unix(from_time)
    #     to_time_unix = datetime_to_unix(to_time)
    #     self.oandadata.get_historical_data(from_time=from_time_unix, to_time=to_time_unix)


    async def fetch_real_time_data(self):
        while True:
            await self.oandadata.get_candle_data()
            await asyncio.sleep(10)


# instruments = ['USD_JPY', 'GBP_JPY', 'EUR_USD', 'GBP_USD']  # Add more instrument names as needed

# data_fetchers = [DataFetcher(instrument) for instrument in instruments]

# loop = asyncio.get_event_loop()
# loop.run_until_complete(asyncio.gather(*(df.fetch_real_time_data() for df in data_fetchers)))


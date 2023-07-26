import sys 
sys.path.insert(0, '/home/andrew/Projects/trading/pair_trade')
import json
import requests
from data_layer.data_feed import OandaAuth

config_file = "config/data_config.json"

# this class creates orders and sends them to Oanda

class Order:
    def __init__(self, auth):
        with open(config_file) as f:
            self.config = json.load(f)
        self.auth = auth
        self.account_id = self.auth.account_id
        self.api_key = self.auth.api_key
        self.base_url = f"https://api-fxtrade.oanda.com/v3/accounts/{self.account_id}/orders"
        self.headers = {
            'Authorization': f'Bearer {self.auth.api_key}',
            'Accept-Datetime-Format': 'RFC3339'
        }

    def create_limit_order(self, 
                       instrument, 
                       units, 
                       price, 
                       type="LIMIT", 
                       timeInForce="GTC", 
                       positionFill="DEFAULT", 
                       triggerCondition="DEFAULT", 
                       gtdTime=None, 
                       clientExtensions=None, 
                       takeProfitOnFill=None, 
                       stopLossOnFill=None, 
                       guaranteedStopLossOnFill=None, 
                       trailingStopLossOnFill=None, 
                       tradeClientExtensions=None):

        # Create the order request data
        data = {
            "order": {
                "type": type,
                "instrument": instrument,
                "units": units,
                "price": price,
                "timeInForce": timeInForce,
                "positionFill": positionFill,
                "triggerCondition": triggerCondition,
                "gtdTime": gtdTime,
                "clientExtensions": clientExtensions,
                "takeProfitOnFill": takeProfitOnFill,
                "stopLossOnFill": stopLossOnFill,
                "guaranteedStopLossOnFill": guaranteedStopLossOnFill,
                "trailingStopLossOnFill": trailingStopLossOnFill,
                "tradeClientExtensions": tradeClientExtensions
            }
        }

        # Send a POST request to the OANDA API
        response = requests.post(self.base_url, headers=self.headers, json=data)

        # Return the response
        print(response.json())
        return response.json()

    def make_stop_loss_json(self, price, distance, timeInForce, gtdTime,clientExtensions):
        return {
            "price": price,
            "distance": distance,
            "timeInForce": timeInForce,
            "gtdTime": gtdTime,
            "clientExtensions": clientExtensions
        }
    
    def make_take_profit_json(self, price, timeInForce, gtdTime,clientExtensions):
        return {
            "price": price,
            "timeInForce": timeInForce,
            "gtdTime": gtdTime,
            "clientExtensions": clientExtensions
        }


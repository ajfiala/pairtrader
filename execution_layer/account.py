import sys 
sys.path.insert(0, '/home/andrew/Projects/trading/pair_trade')
import json
import requests
from data_layer.data_feed import OandaAuth

config_file = "config/data_config.json"

class Account:
    def __init__(self, auth):
        with open(config_file) as f:
            self.config = json.load(f)
        self.auth = auth
        self.account_id = self.auth.account_id
        self.api_key = self.auth.api_key
        self.base_url = f"https://api-fxtrade.oanda.com/v3/accounts/{self.account_id}"
        self.headers = {
            'Authorization': f'Bearer {self.auth.api_key}',
            'Accept-Datetime-Format': 'RFC3339'
        }

    def get_account_summary(self):
        # Get the account summary
        response = requests.get(f"{self.base_url}/summary", headers=self.headers)
        # Return the response
        return response.json()
    
    def get_open_positions(self):
        response = requests.get(f"{self.base_url}/openPositions", headers=self.headers)
        return response.json()
    
    def get_positions(self):
        # returns all positions, even closed ones
        response = requests.get(f"{self.base_url}/positions", headers=self.headers)
        return response.json()
    
# acc = Account(OandaAuth())
# print(acc.get_positions())
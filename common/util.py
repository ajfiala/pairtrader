import os 
import json

def read_config():
    config_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'config.json')

    with open(config_file_path, "r") as config_file:
        return json.load(config_file)

def get_app_config():
    return config['appConfig']

config = read_config()
from pymongo import MongoClient
import re
from common import util

db_config = util.get_app_config()["db"]
MONGODB_HOST = db_config["host"]
MONGODB_PORT = db_config["port"]
MONGODB_USERNAME = db_config["username"]
MONGODB_PASSWORD = db_config["password"]
MONGODB_DB_NAME = db_config["dbName"]

def connect_to_mongodb():
    try:
        client = MongoClient(f"mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}")
        print("Connected successfully!!!")
    except Exception as ex:
        print(f"Error connecting to MongoDB instance: {ex}")

    db = client[f"{MONGODB_DB_NAME}"]
    return db

def get_candlestick_collection(db, instrument):
    return db[f"{instrument}"]
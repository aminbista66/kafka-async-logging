from pymongo import MongoClient
import os

def get_mongo_client():
    client = MongoClient(os.environ.get("MONGO_URI"))
    return client

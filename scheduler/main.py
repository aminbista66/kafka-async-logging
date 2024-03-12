from pymongo import MongoClient
from redis import Redis
import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

mongo_client = MongoClient("mongodb://root:example@localhost:27017/")

database = mongo_client["log_db"]
collection = database["logs"]


redis = Redis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    decode_responses=True,
    db=0,
)


print(redis.get('logs'))


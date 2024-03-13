from pymongo import MongoClient
from redis import Redis
import os


def get_mongo_client():
    mongo_client = MongoClient(os.environ.get("MONGO_URI"))
    return mongo_client


redis = Redis(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    decode_responses=True,
    db=0,
)


def shutdown_db_conn():

    get_mongo_client().close()
    redis.close()

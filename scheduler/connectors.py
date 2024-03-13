from pymongo import MongoClient
from redis import Redis
import os


def get_mongo_client():
    mongo_client = MongoClient(
        "mongodb://root:example@localhost:27017/log_db?authSource=admin"
    )

    database = mongo_client["log_db"]
    db_collection = database["logs"]
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

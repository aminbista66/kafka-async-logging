from connectors import redis, get_mongo_client
from apscheduler.schedulers.background import BackgroundScheduler
import json


def periodic_task():
    print("Running task...")
    response = redis.get("logs")
    if response:
        print("Redis response: {}".format(response))

        logs_in_redis = json.loads(str(response))

        results = (
            get_mongo_client()
            .get_database("log_db")
            .get_collection("logs")
            .insert_many(logs_in_redis)
        )
        print(results)
        redis.delete("logs")
        return
    print("No data found to commit !!")
    return


def run_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(periodic_task, "interval", seconds=60)
    scheduler.start()
    # periodic_task()
    print("Scheduler started !!")

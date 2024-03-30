from fastapi import FastAPI, Request
from datetime import datetime
from .config import startup_callback
from .producer import LogProducer
from .connector import get_mongo_client

producer = LogProducer()
app = FastAPI(on_startup=[startup_callback])


@app.get(path="/get-logs")
def get_logs(request: Request):
    client = get_mongo_client()
    logs = client.get_database("log_db").get_collection("logs").find()
    return [{**log, "_id": str(log["_id"])} for log in logs]


@app.get(path="/action/{action_code}/")
def action(action_code: str):
    action_payload = {"action": action_code, "created_at": str(datetime.now())}
    producer.emit_event(action_payload)
    return {"data": action_payload}

@app.get("/ping")
def ping():
    return "pong"

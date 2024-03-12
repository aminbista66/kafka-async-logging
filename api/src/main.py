from fastapi import FastAPI
from datetime import datetime
from .config import startup_callback
from .producer import LogProducer

app = FastAPI(on_startup=[startup_callback])
producer = LogProducer()


@app.get(path="/get-logs")
def get_logs():
    return [{"logs": "Logs"}]


@app.get(path="/action/{action_code}/")
def action(action_code: str):
    action_payload = {"action": action_code, "created_at": str(datetime.now())}
    producer.emit_event(action_payload)
    return {"data": action_payload}

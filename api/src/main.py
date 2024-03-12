from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get(path='/get-logs')
def get_logs():
    return [{"logs": "Logs"}]

@app.get(path='/action/{action_code}/')
def action(action_code: str):
    action_payload = {
        "action": action_code,
        "created_at": datetime.now()
    }
    return {"data": action_payload}
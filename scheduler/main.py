from fastapi import FastAPI
from config import load_env_callback
from connectors import shutdown_db_conn
from scheduler import run_scheduler

app = FastAPI(
    on_startup=[load_env_callback, run_scheduler], on_shutdown=[shutdown_db_conn]
)


@app.get("/")
def root():
    return {"message": "Scheduler running..."}

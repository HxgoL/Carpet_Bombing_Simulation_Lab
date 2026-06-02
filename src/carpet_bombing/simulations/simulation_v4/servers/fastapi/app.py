from fastapi import FastAPI
from pydantic import BaseModel
from time import time

app = FastAPI(title = "Carpet Bombing Simulation API", version = "1.0")

START_TIME = time()
COMMAND_HISTORY: list[dict] = []

class Command(BaseModel):
    command: str
    target: str | None = None

@app.get("/")
def root():
    return {
        "service": "Carpet Bombing Simulation API",
        "status": "running",
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_seconds": round(time() - START_TIME, 2),
    }

@app.get("/status")
def status():
    return {
        "api": "running",
        "commands_received": len(COMMAND_HISTORY),
    }

@app.post("/command")
def receive_command(command: Command):
    entry = {
        "timestamp": time(),
        "command": command.command,
        "target": command.target,
    }
    COMMAND_HISTORY.append(entry)

    return {
        "accepted": True,
        "received": entry,
    }

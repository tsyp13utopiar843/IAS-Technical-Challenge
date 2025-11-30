from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Alert(BaseModel):
    level: str
    type: str
    source: str
    details: str

# Priority Matrix: Safety > Cyber > Maint > Energy
PRIORITY_MAP = {
    "PPE_VIOLATION": 1,
    "DDoS_RISK": 2,
    "RUL_LOW": 3,
    "ENERGY_OPTIMIZATION": 4
}

@app.post("/plan")
async def create_plan(alert: Alert):
    priority = PRIORITY_MAP.get(alert.type, 5)
    
    action = "LOG_ONLY"
    if priority == 1:
        action = "STOP_MACHINE_IMMEDIATE"
    elif priority == 2:
        action = "ISOLATE_NETWORK_SEGMENT"
    elif priority == 3:
        action = "SCHEDULE_MAINTENANCE_NEXT_SHIFT"
    elif priority == 4:
        action = "ADJUST_POWER_PROFILE"

    return {
        "action": action,
        "priority_level": priority,
        "original_alert": alert
    }

@app.get("/status")
async def get_status():
    return {"state": "nominal", "agent": "Planner"}

import os
import httpx
import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents.utils.notifications import notifier

app = FastAPI()

# Enable CORS for Dashboard
origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PLANNER_URL = os.getenv("PLANNER_URL", "http://localhost:8011")


class Alert(BaseModel):
    level: str
    type: str
    source: str
    details: str


# In-memory store for system state (for Dashboard)
system_state = {
    "alerts": [],
    "decisions": [],
    "last_update": datetime.datetime.utcnow().isoformat(),
}


@app.post("/alert")
async def receive_alert(alert: Alert):
    print(f"Received Alert: {alert}")
    
    # 1. Query Planner
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{PLANNER_URL}/plan", json=alert.dict())
            plan = response.json()
            
            # 2. Log Decision
            decision_record = {
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "alert": alert.dict(),
                "plan": plan,
            }
            system_state["decisions"].insert(0, decision_record)
            system_state["alerts"].insert(0, alert.dict())
            
            # Keep lists trimmed
            system_state["decisions"] = system_state["decisions"][:50]
            system_state["alerts"] = system_state["alerts"][:50]
            
            print(f"Executed Plan: {plan['action']}")
            
            # 3. Trigger Twilio notification for critical alerts
            if alert.level.upper() == "CRITICAL":
                await notifier.send_alert(
                    severity=alert.level,
                    message=alert.details,
                    source_agent=alert.source,
                )

            return {"status": "handled", "action": plan["action"]}
            
    except Exception as e:
        print(f"Error querying planner: {e}")
        return {"status": "error", "details": str(e)}


@app.get("/system-state")
async def get_system_state():
    system_state["last_update"] = datetime.datetime.utcnow().isoformat()
    return system_state


@app.get("/status")
async def get_status():
    return {"state": "nominal", "agent": "Orchestrator"}

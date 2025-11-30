import os
import json
import datetime
import asyncio
import paho.mqtt.client as mqtt
import httpx
from fastapi import FastAPI

app = FastAPI()

# Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))

AGENT_SAFETY_URL = os.getenv("AGENT_SAFETY_URL", "http://localhost:8001")
AGENT_CYBER_URL = os.getenv("AGENT_CYBER_URL", "http://localhost:8002")
AGENT_MAINT_URL = os.getenv("AGENT_MAINT_URL", "http://localhost:8003")
AGENT_ENERGY_URL = os.getenv("AGENT_ENERGY_URL", "http://localhost:8004")

# Mapping data types to Agent URLs
ROUTE_MAP = {
    "vibration": AGENT_MAINT_URL,
    "temp": AGENT_MAINT_URL,
    "power": AGENT_ENERGY_URL,
    "latency": AGENT_CYBER_URL,
    "feed_01": AGENT_SAFETY_URL # Camera feed
}

client = mqtt.Client()

async def forward_to_agent(url, payload):
    async with httpx.AsyncClient() as http_client:
        try:
            await http_client.post(f"{url}/ingest", json=payload)
            # print(f"Forwarded to {url}")
        except Exception as e:
            print(f"Failed to forward to {url}: {e}")

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("factory/#")

def on_message(client, userdata, msg):
    try:
        # Topic: factory/machine_01/telemetry/vibration
        parts = msg.topic.split("/")
        if len(parts) < 4:
            return

        source_id = parts[1]
        data_type = parts[-1] # vibration, temp, power, latency, feed_01
        
        # Handle payload (convert bytes to string/float)
        try:
            value = float(msg.payload)
        except ValueError:
            value = msg.payload.decode("utf-8") # For strings like base64 images

        payload = {
            "source_id": source_id,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "data_type": data_type,
            "value": value,
            "unit": "N/A" # Placeholder
            
            # Let's use sync httpx for simplicity in this callback or fire async in a separate loop
            # BUT, we are inside FastAPI which is async.
            # Best approach for this hybrid: Use a background thread loop or sync call.
            # We'll use sync httpx here to avoid complexity with event loops in callbacks.
            try:
                httpx.post(f"{target_url}/ingest", json=payload)
            except Exception as e:
                print(f"Error forwarding (sync): {e}")

    except Exception as e:
        print(f"Error processing message: {e}")

client.on_connect = on_connect
client.on_message = on_message

@app.on_event("startup")
async def startup_event():
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"Failed to connect to MQTT: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    client.loop_stop()
    client.disconnect()

@app.get("/")
def read_root():
    return {"status": "Protocol Gateway Running"}

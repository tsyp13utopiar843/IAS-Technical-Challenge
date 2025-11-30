import time
import json
import random
import pandas as pd
import numpy as np
import os
import time
import json
import random
import pandas as pd
import numpy as np
from paho.mqtt import client as mqtt_client

broker = os.getenv("MQTT_BROKER", 'broker.emqx.io')
port = int(os.getenv("MQTT_PORT", 1883))
topic_base = "factory"
client_id = f'publish-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    try:
        client.connect(broker, port)
    except Exception as e:
        print(f"Connection failed: {e}")
    return client

def publish(client):
    # Load dataset
    print("Loading dataset...")
    try:
        # Assuming dataset is in the same directory or provided via Docker/Railway
        df = pd.read_csv('manufacturing_6G_dataset.csv')
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    print("Starting publication loop...")
    for index, row in df.iterrows():
        time.sleep(0.1) # Faster simulation for testing
        
        machine_id = row['Machine_ID']
        timestamp = time.time()
        
        # 1. Predictive Maintenance Data
        maint_payload = {
            "timestamp": timestamp,
            "vibration": row['Vibration_Hz'],
            "temperature": row['Temperature_C']
        }
        client.publish(f"{topic_base}/machine/{machine_id}/maintenance", json.dumps(maint_payload))

        # 2. Cyber Threat Data
        net_payload = {
            "timestamp": timestamp,
            "latency": row['Network_Latency_ms'],
            "packet_loss": row['Packet_Loss_%']
        }
        client.publish(f"{topic_base}/network/stats", json.dumps(net_payload))

        # 3. Energy Optimization Data
        energy_payload = {
            "timestamp": timestamp,
            "current_load": row['Power_Consumption_kW']
        }
        client.publish(f"{topic_base}/energy/stats", json.dumps(energy_payload))

        # 4. PPE Detection (Simulated Sensor Data)
        # Simulate 6-axis sensor data
        ppe_payload = {
            "timestamp": timestamp,
            "sensors": np.random.randn(6).tolist(), # Simulated accel/gyro
            "machine_id": machine_id
        }
        client.publish(f"{topic_base}/camera/{machine_id}/ppe", json.dumps(ppe_payload))

        # 5. Full Telemetry for Workplace Hazard & PM Agents
        telemetry_payload = row.to_dict()
        telemetry_payload['timestamp'] = timestamp
        if 'Timestamp' in telemetry_payload:
            del telemetry_payload['Timestamp']
            
        client.publish(f"{topic_base}/machine/{machine_id}/telemetry", json.dumps(telemetry_payload))
        
        if index % 10 == 0:
            print(f"Published data step {index}")

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    client.loop_stop()

if __name__ == '__main__':
    run()

import time
import json
import random
import math
import os
import paho.mqtt.client as mqtt
import base64

# Configuration
BROKER = os.getenv("MQTT_BROKER", "localhost")
PORT = int(os.getenv("MQTT_PORT", 1883))
TOPIC_PREFIX = "factory"

def get_mqtt_client():
    client = mqtt.Client()
    try:
        client.connect(BROKER, PORT, 60)
        return client
    except Exception as e:
        print(f"Could not connect to MQTT Broker: {e}")
        return None

def generate_sine_wave(step, amplitude=1.0, frequency=0.1, noise_level=0.1):
    return amplitude * math.sin(2 * math.pi * frequency * step) + random.uniform(-noise_level, noise_level)

def generate_telemetry(step):
    data = []
    
    # Machine 01 Telemetry
    data.append({
        "topic": f"{TOPIC_PREFIX}/machine_01/telemetry/vibration",
        "value": abs(generate_sine_wave(step, amplitude=0.5, frequency=0.05, noise_level=0.05)) # G-force
    })
    data.append({
        "topic": f"{TOPIC_PREFIX}/machine_01/telemetry/temp",
        "value": 60 + generate_sine_wave(step, amplitude=10, frequency=0.01, noise_level=2) # Celsius
    })
    data.append({
        "topic": f"{TOPIC_PREFIX}/machine_01/telemetry/power",
        "value": 100 + generate_sine_wave(step, amplitude=20, frequency=0.02, noise_level=5) # kW
    })
    
    # 6G Sensor Telemetry
    data.append({
        "topic": f"{TOPIC_PREFIX}/network/6g_sensor_01/latency",
        "value": 5 + random.uniform(0, 2) if random.random() > 0.05 else 50 + random.uniform(0, 20) # ms, occasional spike
    })
    
    # Camera Feed (Mock)
    # Sending a tiny placeholder string as base64 image to avoid massive logs/network load
    mock_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    data.append({
        "topic": f"{TOPIC_PREFIX}/camera/feed_01",
        "value": mock_image
    })

    return data

def main():
    print(f"Starting SCADA Simulator... Connecting to {BROKER}:{PORT}")
    client = get_mqtt_client()
    
    while client is None:
        time.sleep(5)
        client = get_mqtt_client()

    step = 0
    try:
        while True:
            telemetry_batch = generate_telemetry(step)
            for item in telemetry_batch:
                client.publish(item["topic"], item["value"])
                # print(f"Published to {item['topic']}: {item['value']}")
            
            step += 1
            time.sleep(1) # 1Hz publishing rate
    except KeyboardInterrupt:
        print("Stopping SCADA Simulator...")
        client.disconnect()

if __name__ == "__main__":
    main()

"""
MQTT Prediction Simulator
Publishes mock predictions to MQTT for testing the SCADA bridge.
"""
import time
import json
import random
import paho.mqtt.client as mqtt
from datetime import datetime
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as bridge_config


class PredictionSimulator:
    """Simulates AI agent predictions via MQTT."""
    
    def __init__(self):
        self.client = mqtt.Client(client_id="prediction_simulator")
        self.connected = False
    
    def connect(self):
        """Connect to MQTT broker."""
        try:
            print(f"Connecting to MQTT broker at {bridge_config.MQTT_BROKER}:{bridge_config.MQTT_PORT}")
            self.client.connect(bridge_config.MQTT_BROKER, bridge_config.MQTT_PORT, 60)
            self.client.loop_start()
            self.connected = True
            print("Connected successfully")
        except Exception as e:
            print(f"Connection failed: {e}")
            sys.exit(1)
    
    def generate_pm_prediction(self):
        """Generate mock Predictive Maintenance prediction."""
        return {
            "agent_id": "pm_agent",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prediction": {
                "rul_hours": random.uniform(10, 200),
                "health_score": random.uniform(50, 100),
                "alert_level": random.choice(["normal", "warning", "critical"]),
                "failure_probability": random.uniform(0.0, 0.5),
                "recommended_action": random.choice([
                    "No action required",
                    "Schedule maintenance within 48 hours",
                    "Immediate maintenance required",
                    "Monitor closely"
                ])
            }
        }
    
    def generate_energy_prediction(self):
        """Generate mock Energy Optimization prediction."""
        return {
            "agent_id": "energy_agent",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prediction": {
                "consumption_kwh": random.uniform(100, 500),
                "efficiency_score": random.uniform(60, 95),
                "predicted_consumption": random.uniform(100, 500),
                "is_anomaly": random.choice([True, False]),
                "anomaly_score": random.uniform(0, 30)
            }
        }
    
    def generate_cyber_prediction(self):
        """Generate mock Cyber Security prediction."""
        return {
            "agent_id": "cyber_agent",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prediction": {
                "threat_level": random.choice(["low", "medium", "high", "critical"]),
                "anomaly_score": random.uniform(0, 100),
                "active_threats": random.randint(0, 5),
                "network_health": random.uniform(70, 100)
            }
        }
    
    def generate_hazard_prediction(self):
        """Generate mock Workplace Safety prediction."""
        return {
            "agent_id": "hazard_agent",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prediction": {
                "risk_level": random.choice(["low", "medium", "high"]),
                "hazard_count": random.randint(0, 3),
                "safety_score": random.uniform(70, 100),
                "active_warnings": random.randint(0, 5)
            }
        }
    
    def generate_ppe_prediction(self):
        """Generate mock PPE Compliance prediction."""
        return {
            "agent_id": "ppe_agent",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prediction": {
                "compliance_rate": random.uniform(80, 100),
                "violations_count": random.randint(0, 5),
                "workers_monitored": random.randint(10, 50),
                "helmet_compliance": random.uniform(85, 100),
                "vest_compliance": random.uniform(85, 100)
            }
        }
    
    def publish_prediction(self, prediction):
        """Publish prediction to MQTT."""
        agent_id = prediction["agent_id"]
        topic = f"predictions/{agent_id}"
        payload = json.dumps(prediction)
        
        result = self.client.publish(topic, payload)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"✓ Published to {topic}: {prediction['prediction']}")
        else:
            print(f"✗ Failed to publish to {topic}")
    
    def run(self, interval=5, count=None):
        """
        Run simulation loop.
        
        Args:
            interval: Seconds between predictions
            count: Number of predictions to send (None = infinite)
        """
        generators = [
            self.generate_pm_prediction,
            self.generate_energy_prediction,
            self.generate_cyber_prediction,
            self.generate_hazard_prediction,
            self.generate_ppe_prediction
        ]
        
        iteration = 0
        try:
            while count is None or iteration < count:
                print(f"\n--- Iteration {iteration + 1} ---")
                
                # Generate and publish predictions from all agents
                for generator in generators:
                    prediction = generator()
                    self.publish_prediction(prediction)
                    time.sleep(0.1)  # Small delay between agents
                
                iteration += 1
                
                if count is None or iteration < count:
                    print(f"\nWaiting {interval} seconds...")
                    time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n\nSimulation stopped by user")
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        print("Disconnected from MQTT broker")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="MQTT Prediction Simulator")
    parser.add_argument("--interval", type=int, default=5, help="Seconds between predictions (default: 5)")
    parser.add_argument("--count", type=int, default=None, help="Number of iterations (default: infinite)")
    
    args = parser.parse_args()
    
    print("="*60)
    print("MQTT Prediction Simulator")
    print("="*60)
    
    simulator = PredictionSimulator()
    simulator.connect()
    
    try:
        simulator.run(interval=args.interval, count=args.count)
    finally:
        simulator.disconnect()

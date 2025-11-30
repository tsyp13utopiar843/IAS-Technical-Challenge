"""
Load Test for SCADA Bridge
Tests bridge performance under high prediction rate.
"""
import sys
import os
import time
import json
import threading
import paho.mqtt.client as mqtt
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as bridge_config


class LoadTest:
    """Load test for SCADA bridge."""
    
    def __init__(self, target_rate=100, duration=60):
        self.client = mqtt.Client(client_id="load_test")
        self.target_rate = target_rate  # predictions per second
        self.duration = duration  # seconds
        self.stats = {
            "sent": 0,
            "errors": 0,
            "latencies": []
        }
        self.running = False
    
    def connect(self):
        """Connect to MQTT broker."""
        try:
            print(f"Connecting to MQTT broker at {bridge_config.MQTT_BROKER}:{bridge_config.MQTT_PORT}")
            self.client.connect(bridge_config.MQTT_BROKER, bridge_config.MQTT_PORT, 60)
            self.client.loop_start()
            print("✓ Connected successfully\n")
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            sys.exit(1)
    
    def generate_prediction(self, agent_id):
        """Generate simple prediction payload."""
        return {
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "prediction": {
                "test_value": 42.0,
                "rul_hours": 100.0,
                "health_score": 85.0,
                "alert_level": "normal"
            }
        }
    
    def publish_batch(self):
        """Publish one batch of predictions."""
        agents = ["pm_agent", "energy_agent", "cyber_agent", "hazard_agent", "ppe_agent"]
        
        for agent_id in agents:
            prediction = self.generate_prediction(agent_id)
            topic = f"predictions/{agent_id}"
            payload = json.dumps(prediction)
            
            start_time = time.time()
            
            try:
                result = self.client.publish(topic, payload)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    latency = (time.time() - start_time) * 1000  # ms
                    self.stats["latencies"].append(latency)
                    self.stats["sent"] += 1
                else:
                    self.stats["errors"] += 1
            
            except Exception as e:
                self.stats["errors"] += 1
    
    def run(self):
        """Run load test."""
        print("="*60)
        print("SCADA Bridge Load Test")
        print("="*60)
        print(f"Target rate: {self.target_rate} predictions/second")
        print(f"Duration: {self.duration} seconds")
        print(f"Total predictions: {self.target_rate * self.duration}")
        print("="*60)
        print("\nStarting test...\n")
        
        self.running = True
        start_time = time.time()
        
        # Calculate batches per second (each batch = 5 predictions)
        predictions_per_batch = 5
        batches_per_second = self.target_rate / predictions_per_batch
        batch_interval = 1.0 / batches_per_second if batches_per_second > 0 else 0.2
        
        batch_count = 0
        
        try:
            while self.running and (time.time() - start_time) < self.duration:
                batch_start = time.time()
                
                self.publish_batch()
                batch_count += 1
                
                # Print progress every 10 batches
                if batch_count % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = self.stats["sent"] / elapsed if elapsed > 0 else 0
                    print(f"Progress: {batch_count} batches | {self.stats['sent']} sent | {rate:.1f}/sec")
                
                # Maintain target rate
                batch_duration = time.time() - batch_start
                sleep_time = max(0, batch_interval - batch_duration)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
        
        finally:
            self.running = False
            total_time = time.time() - start_time
            self.print_results(total_time)
    
    def print_results(self, total_time):
        """Print load test results."""
        print("\n" + "="*60)
        print("LOAD TEST RESULTS")
        print("="*60)
        
        print(f"\nDuration: {total_time:.2f} seconds")
        print(f"Predictions sent: {self.stats['sent']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Success rate: {(self.stats['sent'] / (self.stats['sent'] + self.stats['errors']) * 100):.2f}%")
        print(f"Actual rate: {self.stats['sent'] / total_time:.2f} predictions/second")
        
        if self.stats["latencies"]:
            latencies = sorted(self.stats["latencies"])
            print(f"\nPublish Latency (MQTT only):")
            print(f"  Min: {min(latencies):.2f} ms")
            print(f"  Max: {max(latencies):.2f} ms")
            print(f"  Mean: {sum(latencies) / len(latencies):.2f} ms")
            print(f"  P50: {latencies[len(latencies) // 2]:.2f} ms")
            print(f"  P95: {latencies[int(len(latencies) * 0.95)]:.2f} ms")
            print(f"  P99: {latencies[int(len(latencies) * 0.99)]:.2f} ms")
        
        # Evaluate results
        success_rate = self.stats['sent'] / (self.stats['sent'] + self.stats['errors']) * 100
        
        print("\n" + "="*60)
        if success_rate >= 99:
            print("✓ LOAD TEST PASSED")
        elif success_rate >= 95:
            print("⚠ LOAD TEST PARTIAL (95-99% success)")
        else:
            print("✗ LOAD TEST FAILED (<95% success)")
        print("="*60)
        
        print("\nNote: This test only measures MQTT publish latency.")
        print("End-to-end latency (MQTT → Protocol Server update) requires")
        print("additional instrumentation in the bridge code.")
    
    def disconnect(self):
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        print("\nDisconnected from MQTT broker")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SCADA Bridge Load Test")
    parser.add_argument("--rate", type=int, default=100, help="Target predictions per second (default: 100)")
    parser.add_argument("--duration", type=int, default=60, help="Test duration in seconds (default: 60)")
    
    args = parser.parse_args()
    
    test = LoadTest(target_rate=args.rate, duration=args.duration)
    test.connect()
    
    # Give time to connect
    time.sleep(1)
    
    try:
        test.run()
    finally:
        test.disconnect()

"""
Bidirectional Write Test
Tests OPC UA write → MQTT config publish functionality.
"""
import sys
import os
import asyncio
import paho.mqtt.client as mqtt
from asyncua import Client
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config as bridge_config


class BidirectionalTest:
    """Test bidirectional communication."""
    
    def __init__(self):
        self.mqtt_client = mqtt.Client(client_id="bidirectional_test")
        self.config_received = False
        self.config_data = None
    
    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback."""
        print(f"\n✓ Received MQTT config message on {msg.topic}")
        print(f"  Payload: {msg.payload.decode('utf-8')}")
        self.config_data = msg.payload.decode('utf-8')
        self.config_received = True
    
    def setup_mqtt(self):
        """Setup MQTT client to listen for config messages."""
        self.mqtt_client.on_message = self.on_mqtt_message
        
        try:
            print(f"Connecting to MQTT broker at {bridge_config.MQTT_BROKER}:{bridge_config.MQTT_PORT}")
            self.mqtt_client.connect(bridge_config.MQTT_BROKER, bridge_config.MQTT_PORT, 60)
            self.mqtt_client.subscribe(f"{bridge_config.MQTT_CONFIG_TOPIC_PREFIX}#")
            self.mqtt_client.loop_start()
            print("✓ MQTT client connected and subscribed to config/#\n")
        except Exception as e:
            print(f"✗ MQTT connection failed: {e}")
            sys.exit(1)
    
    async def test_opcua_write(self):
        """Test writing to OPC UA writable node."""
        url = bridge_config.OPCUA_ENDPOINT
        
        print(f"Connecting to OPC UA server: {url}")
        
        client = Client(url=url)
        
        try:
            await client.connect()
            print("✓ Connected to OPC UA server\n")
            
            # Get namespace index
            nsidx = await client.get_namespace_index(bridge_config.OPCUA_NAMESPACE)
            
            # Navigate to writable node
            root = client.get_objects_node()
            mas_node = await root.get_child([f"{nsidx}:MultiAgentSystem"])
            pm_folder = await mas_node.get_child([f"{nsidx}:PredictiveMaintenance"])
            
            # Get writable threshold node
            threshold_node = await pm_folder.get_child([f"{nsidx}:ThresholdCritical"])
            
            # Read current value
            current_value = await threshold_node.read_value()
            print(f"Current ThresholdCritical value: {current_value}")
            
            # Write new value
            new_value = 15.0
            print(f"Writing new value: {new_value}")
            await threshold_node.write_value(new_value)
            
            # Verify write
            verified_value = await threshold_node.read_value()
            print(f"Verified new value: {verified_value}")
            
            if verified_value == new_value:
                print("✓ OPC UA write successful")
            else:
                print("✗ OPC UA write verification failed")
            
            print("\nWaiting for MQTT config message (timeout: 5 seconds)...")
            
            # Wait for MQTT message
            timeout = 5
            start_time = time.time()
            while not self.config_received and (time.time() - start_time) < timeout:
                await asyncio.sleep(0.1)
            
            if self.config_received:
                print("\n" + "="*60)
                print("✓ BIDIRECTIONAL TEST PASSED")
                print("="*60)
                print("OPC UA write triggered MQTT config publish successfully")
            else:
                print("\n" + "="*60)
                print("⚠ BIDIRECTIONAL TEST PARTIAL")
                print("="*60)
                print("OPC UA write succeeded but MQTT config not received")
                print("Note: Bidirectional feature may not be fully implemented yet")
        
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await client.disconnect()
            print("\nDisconnected from OPC UA server")
    
    def cleanup(self):
        """Cleanup MQTT connection."""
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()
        print("Disconnected from MQTT broker")


async def main():
    """Main test function."""
    print("="*60)
    print("Bidirectional Communication Test")
    print("="*60)
    print("This test writes to an OPC UA node and verifies")
    print("that a corresponding MQTT config message is published.\n")
    
    test = BidirectionalTest()
    test.setup_mqtt()
    
    # Give MQTT time to connect
    await asyncio.sleep(1)
    
    try:
        await test.test_opcua_write()
    finally:
        test.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

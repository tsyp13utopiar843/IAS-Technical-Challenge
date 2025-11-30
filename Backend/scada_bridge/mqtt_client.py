"""
MQTT Client Module
Subscribes to predictions/# topics and distributes to protocol servers.
Supports bidirectional communication (publishes config updates from SCADA writes).
"""
import logging
import time
import threading
from typing import Callable, Dict, Any
import paho.mqtt.client as mqtt
from queue import Queue

from data_transformer import DataTransformer
import config

logger = logging.getLogger(__name__)


class MQTTBridgeClient:
    """MQTT client for the SCADA bridge with retry logic."""
    
    def __init__(self):
        self.client = mqtt.Client(client_id="scada_bridge")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        self.connected = False
        self.message_callbacks = []
        self.transformer = DataTransformer()
        
        # Thread-safe message queue
        self.message_queue = Queue()
        
    def add_message_callback(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        Register a callback for processing MQTT messages.
        Callback signature: callback(agent_id: str, prediction_data: dict)
        """
        self.message_callbacks.append(callback)
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker."""
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}")
            self.connected = True
            
            # Subscribe to predictions topic
            client.subscribe(config.MQTT_PREDICTIONS_TOPIC)
            logger.info(f"Subscribed to {config.MQTT_PREDICTIONS_TOPIC}")
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker."""
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection from MQTT broker. RC: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Callback when MQTT message is received."""
        try:
            # Extract agent_id from topic: predictions/pm_agent -> pm_agent
            topic_parts = msg.topic.split("/")
            if len(topic_parts) < 2:
                logger.warning(f"Invalid topic format: {msg.topic}")
                return
            
            agent_id = topic_parts[1]
            
            # Parse JSON payload
            payload_str = msg.payload.decode("utf-8")
            prediction_data = self.transformer.parse_mqtt_prediction(payload_str)
            
            if prediction_data is None:
                logger.error(f"Failed to parse prediction from {agent_id}")
                return
            
            logger.debug(f"Received prediction from {agent_id}")
            
            # Notify all registered callbacks
            for callback in self.message_callbacks:
                try:
                    callback(agent_id, prediction_data)
                except Exception as e:
                    logger.error(f"Error in message callback: {e}", exc_info=True)
        
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}", exc_info=True)
    
    def connect(self):
        """Connect to MQTT broker with retry logic."""
        retry_count = 0
        while not self.connected:
            try:
                logger.info(f"Attempting to connect to MQTT broker at {config.MQTT_BROKER}:{config.MQTT_PORT}")
                self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, config.MQTT_KEEPALIVE)
                break
            except Exception as e:
                retry_count += 1
                logger.error(f"Connection attempt {retry_count} failed: {e}")
                logger.info(f"Retrying in {config.MQTT_RETRY_DELAY} seconds...")
                time.sleep(config.MQTT_RETRY_DELAY)
    
    def start(self):
        """Start MQTT client loop in background thread."""
        self.connect()
        self.client.loop_start()
        logger.info("MQTT client loop started")
    
    def stop(self):
        """Stop MQTT client gracefully."""
        logger.info("Stopping MQTT client...")
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        logger.info("MQTT client stopped")
    
    def publish_config(self, agent_id: str, config_data: Dict[str, Any]):
        """
        Publish configuration update to MQTT for an agent.
        Used when SCADA writes to writable nodes.
        """
        import json
        try:
            topic = f"{config.MQTT_CONFIG_TOPIC_PREFIX}{agent_id}"
            payload = json.dumps(config_data)
            result = self.client.publish(topic, payload)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"Published config to {topic}: {config_data}")
            else:
                logger.error(f"Failed to publish config to {topic}. RC: {result.rc}")
        
        except Exception as e:
            logger.error(f"Error publishing config: {e}", exc_info=True)

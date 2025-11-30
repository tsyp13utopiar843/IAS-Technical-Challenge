"""
MQTT Client Utility
Reusable MQTT client for agent communication.
"""
import paho.mqtt.client as mqtt
from typing import Callable, Dict, Any, List, Optional
import logging
import json
import time

# Handle paho-mqtt version differences
try:
    from paho.mqtt.enums import CallbackAPIVersion
    HAS_V2_ENUMS = True
except ImportError:
    # paho-mqtt < 2.0 doesn't have enums module
    HAS_V2_ENUMS = False
    CallbackAPIVersion = None

logger = logging.getLogger("MQTTClient")


class MQTTClientWrapper:
    """Wrapper for paho MQTT client with reconnection and error handling."""
    
    def __init__(self, client_id: str, broker: str, port: int = 1883, keepalive: int = 60):
        """
        Initialize MQTT client wrapper.
        
        Args:
            client_id: MQTT client identifier
            broker: MQTT broker hostname
            port: MQTT broker port
            keepalive: Keep-alive interval in seconds
        """
        self.client_id = client_id
        self.broker = broker
        self.port = port
        self.keepalive = keepalive
        
        # Create client with appropriate API version
        if HAS_V2_ENUMS:
            self.client = mqtt.Client(client_id=client_id, callback_api_version=CallbackAPIVersion.VERSION2)
        else:
            # paho-mqtt 1.x uses different API
            self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        self.connected = False
        self.subscribe_topics: List[str] = []
        self.message_callback: Optional [Callable] = None
        
    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Handle MQTT connection."""
        # Handle both v1.x and v2.x callback signatures
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
            self.connected = True
            
            # Re-subscribe to topics
            for topic in self.subscribe_topics:
                client.subscribe(topic)
                logger.info(f"Subscribed to {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code {rc}")
            self.connected = False
    
    def _on_disconnect(self, client, userdata, rc, properties=None):
        """Handle MQTT disconnection."""
        # Handle both v1.x and v2.x callback signatures
        self.connected = False
        if rc != 0:
            logger.warning(f"Unexpected disconnection, return code {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT message."""
        try:
            if self.message_callback:
                self.message_callback(msg.topic, msg.payload)
        except Exception as e:
            logger.error(f"Error in message callback: {e}", exc_info=True)
    
    def connect(self, retry_count: int = 5, retry_delay: int = 5) -> bool:
        """
        Connect to MQTT broker with retries.
        
        Args:
            retry_count: Number of connection attempts
            retry_delay: Seconds between retries
        
        Returns:
            True if connected successfully
        """
        for attempt in range(retry_count):
            try:
                logger.info(f"Connecting to MQTT broker at {self.broker}:{self.port} (attempt {attempt + 1}/{retry_count})")
                self.client.connect(self.broker, self.port, self.keepalive)
                self.client.loop_start()
                
                # Wait for connection
                for _ in range(10):
                    if self.connected:
                        return True
                    time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < retry_count - 1:
                    time.sleep(retry_delay)
        
        logger.error(f"Failed to connect after {retry_count} attempts")
        return False
    
    def disconnect(self) -> None:
        """Disconnect from MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        self.connected = False
        logger.info("Disconnected from MQTT broker")
    
    def subscribe(self, topics: List[str]) -> None:
        """
        Subscribe to MQTT topics.
        
        Args:
            topics: List of topic patterns to subscribe to
        """
        self.subscribe_topics.extend(topics)
        
        if self.connected:
            for topic in topics:
                self.client.subscribe(topic)
                logger.info(f"Subscribed to {topic}")
    
    def publish(self, topic: str, payload: Any, qos: int = 0) -> bool:
        """
        Publish message to MQTT topic.
        
        Args:
            topic: MQTT topic
            payload: Message payload (will be JSON encoded if dict)
            qos: Quality of Service level
        
        Returns:
            True if published successfully
        """
        if not self.connected:
            logger.warning("Not connected to MQTT broker")
            return False
        
        try:
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            elif not isinstance(payload, (str, bytes)):
                payload = str(payload)
            
            result = self.client.publish(topic, payload, qos=qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {topic}")
                return True
            else:
                logger.error(f"Failed to publish to {topic}, rc={result.rc}")
                return False
        
        except Exception as e:
            logger.error(f"Error publishing to {topic}: {e}")
            return False
    
    def set_message_callback(self, callback: Callable[[str, bytes], None]) -> None:
        """
        Set callback for incoming messages.
        
        Args:
            callback: Function(topic: str, payload: bytes)
        """
        self.message_callback = callback

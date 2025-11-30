"""
Backlog Agent Communication Component
Handles MQTT subscriptions to collect alerts and publish backlogs.
"""
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import asyncio

from agents.utils.mqtt_client import MQTTClientWrapper

logger = logging.getLogger("BacklogAgent.Communication")


class BacklogCommunication:
    """
    Backlog Generation Communication Component.
    
    Subscribes to alert topics from all agents to collect violations and anomalies.
    Publishes generated backlogs to MQTT.
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any], 
                 event_callback: Optional[Callable] = None):
        """
        Initialize communication component.
        
        Args:
            agent_id: Agent identifier
            config: Communication configuration
            event_callback: Callback function for processing collected events
        """
        self.agent_id = agent_id
        self.config = config
        self.event_callback = event_callback
        
        # MQTT client
        mqtt_config = config.get('mqtt', {})
        broker = mqtt_config.get('broker', 'localhost')
        port = mqtt_config.get('port', 1883)
        
        self.mqtt_client = MQTTClientWrapper(
            client_id=f"{agent_id}_client",
            broker=broker,
            port=port
        )
        
        # Subscribe to all agent alert topics
        self.subscribe_topics = mqtt_config.get('subscribe_topics', [
            'alerts/pm_agent',
            'alerts/energy_agent',
            'alerts/cyber_agent',
            'alerts/hazard_agent',
            'alerts/ppe_agent'
        ])
        
        self.publish_topic = mqtt_config.get('publish_topics', ['backlogs/shift_backlog'])[0]
        
        # FastAPI app
        self.app = FastAPI(title=f"{agent_id} API")
        self.api_port = config.get('api', {}).get('port', 8006)
        
        # State references (set by agent)
        self.state = None
        
        # Setup API routes
        self._setup_routes()
        
        logger.info(f"Initialized Backlog Communication (MQTT: {broker}:{port}, API: {self.api_port})")
    
    def _setup_routes(self) -> None:
        """Setup FastAPI routes."""
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "agent_id": self.agent_id,
                "mqtt_connected": self.mqtt_client.connected
            }
        
        @self.app.get("/status")
        async def get_status():
            if self.state:
                return self.state.get_state()
            return {"status": "unknown", "agent_id": self.agent_id}
        
        @self.app.get("/current_shift")
        async def get_current_shift():
            """Get current shift information."""
            if self.state:
                shift_start = self.state.get_current_shift_start()
                events = self.state.get_current_shift_events()
                return {
                    "shift_start": shift_start.isoformat(),
                    "events_count": len(events),
                    "events": events[-10:]  # Last 10 events
                }
            return {"error": "State not available"}
        
        @self.app.get("/backlog_history")
        async def get_backlog_history(limit: int = 10):
            """Get backlog generation history."""
            if self.state:
                state = self.state.get_state()
                history = state.get('custom_state', {}).get('backlog_history', [])
                return {"history": history[-limit:]}
            return {"history": []}
    
    async def start_communication(self) -> None:
        """Start communication interfaces."""
        if not self.mqtt_client.connect():
            logger.error("Failed to connect to MQTT broker")
        else:
            if self.subscribe_topics:
                self.mqtt_client.subscribe(self.subscribe_topics)
                logger.info(f"Subscribed to {len(self.subscribe_topics)} alert topics")
            self.mqtt_client.set_message_callback(self._on_mqtt_message)
        
        config = uvicorn.Config(self.app, host="0.0.0.0", port=self.api_port, log_level="info")
        self.server = uvicorn.Server(config)
        self.server_task = asyncio.create_task(self.server.serve())
        logger.info(f"Communication interfaces started (API on port {self.api_port})")
    
    async def stop_communication(self) -> None:
        """Stop communication interfaces gracefully."""
        self.mqtt_client.disconnect()
        
        if hasattr(self, 'server_task'):
            self.server.should_exit = True
            try:
                await self.server_task
            except Exception as e:
                logger.error(f"Error stopping API server: {e}")
        
        logger.info("Communication interfaces stopped")
    
    def _on_mqtt_message(self, topic: str, payload: bytes) -> None:
        """
        Handle incoming MQTT alert message.
        
        Collects alerts from all agents for backlog generation.
        """
        try:
            message = json.loads(payload.decode('utf-8'))
            logger.debug(f"Received alert on {topic}: {message.get('alert_level', 'UNKNOWN')}")
            
            # Extract agent_id from topic or message
            agent_id = message.get('agent_id', 'unknown')
            if agent_id == 'unknown':
                # Try to extract from topic
                for agent in ['pm_agent', 'energy_agent', 'cyber_agent', 'hazard_agent', 'ppe_agent']:
                    if agent in topic:
                        agent_id = agent
                        break
            
            # Create event structure
            event = {
                "agent_id": agent_id,
                "alert_level": message.get('alert_level', message.get('severity', 'UNKNOWN')),
                "timestamp": message.get('timestamp', message.get('data', {}).get('timestamp')),
                "message": message.get('message', ''),
                "data": message.get('data', {}),
                "topic": topic
            }
            
            # Trigger event callback if available
            if self.event_callback:
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(self.event_callback(event))
                    else:
                        loop.run_until_complete(self.event_callback(event))
                except RuntimeError:
                    asyncio.run(self.event_callback(event))
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode MQTT message: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}", exc_info=True)
    
    async def publish_backlog(self, backlog: Dict[str, Any]) -> None:
        """
        Publish generated backlog to MQTT topic.
        
        Args:
            backlog: Generated backlog dictionary
        """
        try:
            message = {
                "agent_id": self.agent_id,
                "timestamp": backlog.get('generated_at'),
                "backlog": backlog
            }
            
            success = self.mqtt_client.publish(self.publish_topic, message, qos=1)
            if success:
                logger.info(f"Published backlog to {self.publish_topic}")
            else:
                logger.warning(f"Failed to publish backlog to {self.publish_topic}")
            
        except Exception as e:
            logger.error(f"Error publishing backlog: {e}", exc_info=True)


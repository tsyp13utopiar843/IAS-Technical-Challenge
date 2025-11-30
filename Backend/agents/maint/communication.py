"""
PM Agent Communication Component
Handles MQTT, REST API, and WebSocket interfaces.
"""
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import uvicorn
import asyncio

from agents.utils.mqtt_client import MQTTClientWrapper

logger = logging.getLogger("PMAgent.Communication")


class PMCommunication:
    """
    Predictive Maintenance Communication Component.
    
    Manages MQTT subscriptions/publishing, REST API endpoints, and WebSocket streaming.
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any], 
                 prediction_callback: Optional[Callable] = None):
        """
        Initialize communication component.
        
        Args:
            agent_id: Agent identifier
            config: Communication configuration
            prediction_callback: Callback function for processing predictions
        """
        self.agent_id = agent_id
        self.config = config
        self.prediction_callback = prediction_callback
        
        # MQTT client
        mqtt_config = config.get('mqtt', {})
        broker = mqtt_config.get('broker', 'localhost')
        port = mqtt_config.get('port', 1883)
        
        self.mqtt_client = MQTTClientWrapper(
            client_id=f"{agent_id}_client",
            broker=broker,
            port=port
        )
        
        # Subscribe topics
        self.subscribe_topics = mqtt_config.get('subscribe_topics', [])
        self.publish_topic = mqtt_config.get('publish_topics', ['predictions/pm_agent'])[0]
        
        # FastAPI app
        self.app = FastAPI(title=f"{agent_id} API")
        self.api_port = config.get('api', {}).get('port', 8001)
        
        # WebSocket connections
        self.websocket_connections: List[WebSocket] = []
        
        # State references (set by agent)
        self.state = None
        self.model = None
        
        # Setup API routes
        self._setup_routes()
        
        logger.info(f"Initialized PM Communication (MQTT: {broker}:{port}, API: {self.api_port})")
    
    def _setup_routes(self) -> None:
        """Setup FastAPI routes."""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {
                "status": "healthy",
                "agent_id": self.agent_id,
                "mqtt_connected": self.mqtt_client.connected
            }
        
        @self.app.get("/status")
        async def get_status():
            """Get agent status."""
            if self.state:
                return self.state.get_state()
            return {"status": "unknown", "agent_id": self.agent_id}
        
        @self.app.post("/predict")
        async def manual_predict(data: Dict[str, Any]):
            """Manual prediction endpoint."""
            if not self.prediction_callback:
                return JSONResponse(
                    status_code=503,
                    content={"error": "Prediction callback not available"}
                )
            
            try:
                # Trigger prediction callback
                await self.prediction_callback(data)
                return {"status": "prediction_triggered"}
            except Exception as e:
                logger.error(f"Manual prediction error: {e}", exc_info=True)
                return JSONResponse(
                    status_code=500,
                    content={"error": str(e)}
                )
        
        @self.app.get("/history")
        async def get_history(limit: int = 10):
            """Get prediction history."""
            if self.state:
                state = self.state.get_state()
                history = state.get('prediction_history', [])
                return {"history": history[-limit:]}
            return {"history": []}
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time prediction streaming."""
            await websocket.accept()
            self.websocket_connections.append(websocket)
            logger.info(f"WebSocket client connected (total: {len(self.websocket_connections)})")
            
            try:
                while True:
                    # Keep connection alive and wait for messages
                    data = await websocket.receive_text()
                    # Echo back (or handle commands)
                    await websocket.send_text(json.dumps({"status": "received", "data": data}))
            except WebSocketDisconnect:
                self.websocket_connections.remove(websocket)
                logger.info(f"WebSocket client disconnected (remaining: {len(self.websocket_connections)})")
    
    async def start_communication(self) -> None:
        """Start communication interfaces."""
        # Start MQTT
        if not self.mqtt_client.connect():
            logger.error("Failed to connect to MQTT broker")
        else:
            # Subscribe to topics
            if self.subscribe_topics:
                self.mqtt_client.subscribe(self.subscribe_topics)
            
            # Set message callback
            self.mqtt_client.set_message_callback(self._on_mqtt_message)
        
        # Start FastAPI server
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=self.api_port,
            log_level="info"
        )
        self.server = uvicorn.Server(config)
        
        # Run server in background
        self.server_task = asyncio.create_task(self.server.serve())
        
        logger.info(f"Communication interfaces started (API on port {self.api_port})")
    
    async def stop_communication(self) -> None:
        """Stop communication interfaces gracefully."""
        # Stop MQTT
        self.mqtt_client.disconnect()
        
        # Stop FastAPI server
        if hasattr(self, 'server_task'):
            self.server.should_exit = True
            try:
                await self.server_task
            except Exception as e:
                logger.error(f"Error stopping API server: {e}")
        
        # Close WebSocket connections
        for ws in self.websocket_connections:
            try:
                await ws.close()
            except Exception:
                pass
        self.websocket_connections.clear()
        
        logger.info("Communication interfaces stopped")
    
    def _on_mqtt_message(self, topic: str, payload: bytes) -> None:
        """
        Handle incoming MQTT message.
        
        Args:
            topic: MQTT topic
            payload: Message payload (bytes)
        """
        try:
            # Decode payload
            message = json.loads(payload.decode('utf-8'))
            logger.debug(f"Received MQTT message on {topic}: {message}")
            
            # Trigger prediction callback if available
            if self.prediction_callback:
                # Schedule async callback
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # Create task if loop is running
                        asyncio.create_task(self.prediction_callback(message))
                    else:
                        # Run if loop is not running
                        loop.run_until_complete(self.prediction_callback(message))
                except RuntimeError:
                    # No event loop, create new one
                    asyncio.run(self.prediction_callback(message))
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode MQTT message: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}", exc_info=True)
    
    async def publish_prediction(self, prediction: Dict[str, Any]) -> None:
        """
        Publish prediction to MQTT topic.
        
        Args:
            prediction: Prediction dictionary to publish
        """
        try:
            # Format prediction message
            message = {
                "agent_id": self.agent_id,
                "timestamp": prediction.get('timestamp'),
                "prediction": {
                    "rul_hours": prediction.get('rul_hours'),
                    "health_score": prediction.get('health_score'),
                    "failure_probability": prediction.get('failure_probability'),
                    "confidence": prediction.get('confidence'),
                    "alert_level": prediction.get('alert_level'),
                    "action": prediction.get('action'),
                    "recommended_action": prediction.get('recommended_action')
                }
            }
            
            # Publish to MQTT
            success = self.mqtt_client.publish(self.publish_topic, message, qos=1)
            
            if success:
                logger.debug(f"Published prediction to {self.publish_topic}")
            else:
                logger.warning(f"Failed to publish prediction to {self.publish_topic}")
            
            # Broadcast to WebSocket connections
            await self._broadcast_websocket(message)
            
        except Exception as e:
            logger.error(f"Error publishing prediction: {e}", exc_info=True)
    
    async def _broadcast_websocket(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all WebSocket connections."""
        if not self.websocket_connections:
            return
        
        disconnected = []
        for ws in self.websocket_connections:
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                disconnected.append(ws)
        
        # Remove disconnected clients
        for ws in disconnected:
            if ws in self.websocket_connections:
                self.websocket_connections.remove(ws)


"""
PPE Agent Communication Component
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

logger = logging.getLogger("PPEAgent.Communication")


class PPECommunication:
    """PPE Compliance Detection Communication Component."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any], 
                 prediction_callback: Optional[Callable] = None):
        """Initialize communication component."""
        self.agent_id = agent_id
        self.config = config
        self.prediction_callback = prediction_callback
        
        mqtt_config = config.get('mqtt', {})
        broker = mqtt_config.get('broker', 'localhost')
        port = mqtt_config.get('port', 1883)
        
        self.mqtt_client = MQTTClientWrapper(
            client_id=f"{agent_id}_client",
            broker=broker,
            port=port
        )
        
        self.subscribe_topics = mqtt_config.get('subscribe_topics', [])
        self.publish_topic = mqtt_config.get('publish_topics', ['predictions/ppe_agent'])[0]
        
        self.app = FastAPI(title=f"{agent_id} API")
        self.api_port = config.get('api', {}).get('port', 8005)
        
        self.websocket_connections: List[WebSocket] = []
        self.state = None
        self.model = None
        
        self._setup_routes()
        logger.info(f"Initialized PPE Communication (MQTT: {broker}:{port}, API: {self.api_port})")
    
    def _setup_routes(self) -> None:
        """Setup FastAPI routes."""
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "agent_id": self.agent_id, "mqtt_connected": self.mqtt_client.connected}
        
        @self.app.get("/status")
        async def get_status():
            if self.state:
                return self.state.get_state()
            return {"status": "unknown", "agent_id": self.agent_id}
        
        @self.app.post("/predict")
        async def manual_predict(data: Dict[str, Any]):
            if not self.prediction_callback:
                return JSONResponse(status_code=503, content={"error": "Prediction callback not available"})
            try:
                await self.prediction_callback(data)
                return {"status": "prediction_triggered"}
            except Exception as e:
                logger.error(f"Manual prediction error: {e}", exc_info=True)
                return JSONResponse(status_code=500, content={"error": str(e)})
        
        @self.app.get("/history")
        async def get_history(limit: int = 10):
            if self.state:
                state = self.state.get_state()
                history = state.get('prediction_history', [])
                return {"history": history[-limit:]}
            return {"history": []}
        
        @self.app.get("/worker/{worker_id}/compliance")
        async def get_worker_compliance(worker_id: str):
            if self.state:
                state = self.state.get_state()
                worker_compliance = state.get('custom_state', {}).get('worker_compliance', {})
                return worker_compliance.get(worker_id, {})
            return {}
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.websocket_connections.append(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    await websocket.send_text(json.dumps({"status": "received", "data": data}))
            except WebSocketDisconnect:
                self.websocket_connections.remove(websocket)
    
    async def start_communication(self) -> None:
        """Start communication interfaces."""
        if not self.mqtt_client.connect():
            logger.error("Failed to connect to MQTT broker")
        else:
            if self.subscribe_topics:
                self.mqtt_client.subscribe(self.subscribe_topics)
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
            except Exception:
                pass
        for ws in self.websocket_connections:
            try:
                await ws.close()
            except Exception:
                pass
        self.websocket_connections.clear()
        logger.info("Communication interfaces stopped")
    
    def _on_mqtt_message(self, topic: str, payload: bytes) -> None:
        """Handle incoming MQTT message."""
        try:
            message = json.loads(payload.decode('utf-8'))
            logger.debug(f"Received MQTT message on {topic}: {message}")
            if self.prediction_callback:
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(self.prediction_callback(message))
                    else:
                        loop.run_until_complete(self.prediction_callback(message))
                except RuntimeError:
                    asyncio.run(self.prediction_callback(message))
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode MQTT message: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}", exc_info=True)
    
    async def publish_prediction(self, prediction: Dict[str, Any]) -> None:
        """Publish prediction to MQTT topic."""
        try:
            message = {
                "agent_id": self.agent_id,
                "timestamp": prediction.get('timestamp'),
                "prediction": {
                    "helmet_compliant": prediction.get('helmet_compliant'),
                    "vest_compliant": prediction.get('vest_compliant'),
                    "gloves_compliant": prediction.get('gloves_compliant'),
                    "overall_compliance": prediction.get('overall_compliance'),
                    "compliance_rate": prediction.get('compliance_rate'),
                    "alert_level": prediction.get('alert_level'),
                    "action": prediction.get('action'),
                    "access_denied": prediction.get('access_denied', False),
                    "violations": prediction.get('violations', [])
                }
            }
            success = self.mqtt_client.publish(self.publish_topic, message, qos=1)
            if success:
                logger.debug(f"Published prediction to {self.publish_topic}")
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
        for ws in disconnected:
            if ws in self.websocket_connections:
                self.websocket_connections.remove(ws)


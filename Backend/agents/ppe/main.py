"""
PPE Agent Main Orchestrator
PPE Compliance Detection Agent - Main entry point and orchestrator.
"""
import asyncio
import logging
import signal
import sys
import os
from typing import Dict, Any

from agents.base_agent import BaseAgent
from agents.utils.config_loader import load_agent_config
from agents.ppe.model import PPEModel
from agents.ppe.logic import PPELogic
from agents.ppe.state import PPEState
from agents.ppe.communication import PPECommunication
from agents.ppe.alerts import PPEAlerts

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("PPEAgent")


class PPEAgent(BaseAgent):
    """PPE Compliance Detection Agent."""
    
    def __init__(self, config: Dict[str, Any]):
        agent_id = config.get('agent', {}).get('id', 'ppe_agent')
        super().__init__(agent_id, config)
        self._init_components()
        logger.info(f"PPE Agent initialized: {agent_id}")
    
    def _init_components(self) -> None:
        model_config = self.config.get('model', {})
        self.model = PPEModel(
            model_path=model_config.get('path', 'artifacts/ppe_model.pkl'),
            sequence_length=model_config.get('sequence_length', 10),
            num_features=model_config.get('num_features', 6),
            smoothing_buffer_size=model_config.get('smoothing_buffer_size', 5),
            scaler_path=model_config.get('scaler_path'),
            class_weights_path=model_config.get('class_weights_path')
        )
        
        logic_config = self.config.get('logic', {})
        self.logic = PPELogic(logic_config.get('thresholds', {}))
        
        state_config = self.config.get('state', {})
        self.state = PPEState(
            agent_id=self.agent_id,
            buffer_size=state_config.get('buffer_size', 100),
            checkpoint_interval=state_config.get('checkpoint_interval', 300),
            checkpoint_path=state_config.get('checkpoint_path', 'state/ppe_agent_state.json')
        )
        
        comm_config = self.config.get('communication', {})
        self.communication = PPECommunication(
            agent_id=self.agent_id,
            config=comm_config,
            prediction_callback=self._process_sensor_data
        )
        self.communication.state = self.state
        self.communication.model = self.model
        
        alerts_config = self.config.get('alerts', {})
        self.alerts = PPEAlerts(
            agent_id=self.agent_id,
            config=alerts_config,
            mqtt_client=self.communication.mqtt_client
        )
        logger.info("All components initialized")
    
    def load_model(self, model_path: str) -> None:
        self.model.model_path = model_path
        self.model.load_model()
    
    def preprocess(self, raw_data: Any) -> Any:
        return self.model.preprocess(raw_data)
    
    def predict(self, preprocessed_data: Any) -> Dict[str, Any]:
        return self.model.predict(preprocessed_data)
    
    def apply_logic(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        return self.logic.apply_logic(prediction)
    
    def update_state(self, prediction: Dict[str, Any], logic_output: Dict[str, Any]) -> None:
        self.state.update(prediction, logic_output)
    
    def get_state(self) -> Dict[str, Any]:
        return self.state.get_state()
    
    def save_state(self, filepath: str) -> None:
        self.state.save_state(filepath)
    
    def load_state(self, filepath: str) -> None:
        self.state.load_state(filepath)
    
    async def start_communication(self) -> None:
        await self.communication.start_communication()
    
    async def stop_communication(self) -> None:
        await self.communication.stop_communication()
    
    async def publish_prediction(self, prediction: Dict[str, Any]) -> None:
        await self.communication.publish_prediction(prediction)
    
    async def handle_alerts(self, logic_output: Dict[str, Any]) -> None:
        await self.alerts.handle_alerts(logic_output)
    
    async def _process_sensor_data(self, sensor_data: Dict[str, Any]) -> None:
        try:
            logger.debug(f"Processing sensor data: {sensor_data}")
            preprocessed = self.preprocess(sensor_data)
            if preprocessed is None:
                logger.debug("Insufficient data for prediction")
                return
            
            prediction = self.predict(preprocessed)
            logger.info(f"Prediction: Compliance={prediction.get('compliance_rate')}%, "
                       f"Overall={prediction.get('overall_compliance')}")
            
            logic_output = self.apply_logic(prediction)
            logger.info(f"Logic output: {logic_output.get('alert_level')} - {logic_output.get('action')}")
            
            # Add worker_id to prediction if available
            if 'worker_id' in sensor_data:
                prediction['worker_id'] = sensor_data['worker_id']
            
            self.update_state(prediction, logic_output)
            combined = {**prediction, **logic_output}
            await self.publish_prediction(combined)
            await self.handle_alerts(logic_output)
            
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}", exc_info=True)
            self.state.update({}, {"alert_level": "ERROR"}, success=False)
    
    async def initialize(self) -> None:
        await super().initialize()
        model_path = self.config.get('model', {}).get('path')
        if model_path:
            self.load_model(model_path)
        state_path = self.config.get('state', {}).get('checkpoint_path')
        if state_path:
            self.load_state(state_path)
        await self.state.start_checkpointing()
        logger.info("PPE Agent initialized successfully")
    
    async def stop(self) -> None:
        await self.state.stop_checkpointing()
        state_path = self.config.get('state', {}).get('checkpoint_path')
        if state_path:
            self.save_state(state_path)
        await super().stop()


async def main():
    """Main entry point."""
    agents_dir = os.path.dirname(os.path.dirname(__file__))
    config_dir = os.path.join(agents_dir, 'config')
    config = load_agent_config('ppe_agent', config_dir)
    
    ppe_dir = os.path.dirname(__file__)
    backend_root = os.path.dirname(os.path.dirname(ppe_dir))
    
    if 'model' in config:
        model_path = config['model'].get('path', 'artifacts/ppe_model.pkl')
        if not os.path.isabs(model_path):
            full_path = os.path.join(ppe_dir, model_path)
            if not os.path.exists(full_path):
                full_path = os.path.join(backend_root, model_path.replace('../', ''))
            config['model']['path'] = full_path
        
        scaler_path = config['model'].get('scaler_path')
        if scaler_path and not os.path.isabs(scaler_path):
            full_path = os.path.join(ppe_dir, scaler_path)
            if not os.path.exists(full_path):
                full_path = os.path.join(backend_root, scaler_path.replace('../', ''))
            config['model']['scaler_path'] = full_path
        
        class_weights_path = config['model'].get('class_weights_path')
        if class_weights_path and not os.path.isabs(class_weights_path):
            full_path = os.path.join(ppe_dir, class_weights_path)
            if not os.path.exists(full_path):
                full_path = os.path.join(backend_root, class_weights_path.replace('../', ''))
            config['model']['class_weights_path'] = full_path
    
    if 'state' in config:
        state_path = config['state'].get('checkpoint_path', 'state/ppe_agent_state.json')
        if not os.path.isabs(state_path):
            state_dir = os.path.join(ppe_dir, 'state')
            os.makedirs(state_dir, exist_ok=True)
            config['state']['checkpoint_path'] = os.path.join(state_dir, 'ppe_agent_state.json')
    
    if 'MQTT_BROKER' in os.environ:
        config['communication']['mqtt']['broker'] = os.environ['MQTT_BROKER']
    if 'MQTT_PORT' in os.environ:
        config['communication']['mqtt']['port'] = int(os.environ['MQTT_PORT'])
    
    agent = PPEAgent(config)
    
    shutdown_event = asyncio.Event()
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        shutdown_event.set()
    
    if sys.platform != 'win32':
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await agent.start()
        logger.info("PPE Agent started. Press Ctrl+C to stop.")
        try:
            await shutdown_event.wait()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except asyncio.CancelledError:
            pass
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await agent.stop()
        logger.info("PPE Agent stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")

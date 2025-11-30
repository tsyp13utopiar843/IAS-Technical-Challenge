"""
Energy Agent Main Orchestrator
Energy Consumption Optimization Agent - Main entry point and orchestrator.
"""
import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
from typing import Dict, Any

from agents.base_agent import BaseAgent
from agents.utils.config_loader import load_agent_config
from agents.energy.model import EnergyModel
from agents.energy.logic import EnergyLogic
from agents.energy.state import EnergyState
from agents.energy.communication import EnergyCommunication
from agents.energy.alerts import EnergyAlerts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EnergyAgent")


class EnergyAgent(BaseAgent):
    """
    Energy Consumption Optimization Agent.
    
    Monitors energy consumption using LSTM + Isolation Forest models,
    detects anomalies, calculates efficiency scores, and provides
    optimization recommendations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Energy Agent."""
        agent_id = config.get('agent', {}).get('id', 'energy_agent')
        super().__init__(agent_id, config)
        self._init_components()
        logger.info(f"Energy Agent initialized: {agent_id}")
    
    def _init_components(self) -> None:
        """Initialize all 5 components."""
        # Model component
        model_config = self.config.get('model', {})
        self.model = EnergyModel(
            model_path=model_config.get('path', 'artifacts/model.pkl'),
            anomaly_model_path=model_config.get('anomaly_model_path'),
            sequence_length=model_config.get('sequence_length', 60),
            num_features=model_config.get('num_features', 5)
        )
        
        # Logic component
        logic_config = self.config.get('logic', {})
        self.logic = EnergyLogic(logic_config.get('thresholds', {}))
        
        # State component
        state_config = self.config.get('state', {})
        self.state = EnergyState(
            agent_id=self.agent_id,
            buffer_size=state_config.get('buffer_size', 100),
            checkpoint_interval=state_config.get('checkpoint_interval', 300),
            checkpoint_path=state_config.get('checkpoint_path', 'state/energy_agent_state.json')
        )
        
        # Communication component
        comm_config = self.config.get('communication', {})
        self.communication = EnergyCommunication(
            agent_id=self.agent_id,
            config=comm_config,
            prediction_callback=self._process_sensor_data
        )
        self.communication.state = self.state
        self.communication.model = self.model
        
        # Alerts component
        alerts_config = self.config.get('alerts', {})
        self.alerts = EnergyAlerts(
            agent_id=self.agent_id,
            config=alerts_config,
            mqtt_client=self.communication.mqtt_client
        )
        
        logger.info("All components initialized")
    
    # ==================== MODEL COMPONENT IMPLEMENTATION ====================
    
    def load_model(self, model_path: str) -> None:
        """Load model from path."""
        self.model.model_path = model_path
        self.model.load_model()
    
    def preprocess(self, raw_data: Any) -> Any:
        """Preprocess raw sensor data."""
        return self.model.preprocess(raw_data)
    
    def predict(self, preprocessed_data: Any) -> Dict[str, Any]:
        """Run model inference."""
        return self.model.predict(preprocessed_data)
    
    # ==================== LOGIC COMPONENT IMPLEMENTATION ====================
    
    def apply_logic(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules to prediction."""
        return self.logic.apply_logic(prediction)
    
    # ==================== STATE COMPONENT IMPLEMENTATION ====================
    
    def update_state(self, prediction: Dict[str, Any], logic_output: Dict[str, Any]) -> None:
        """Update agent state."""
        self.state.update(prediction, logic_output)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state."""
        return self.state.get_state()
    
    def save_state(self, filepath: str) -> None:
        """Save state to disk."""
        self.state.save_state(filepath)
    
    def load_state(self, filepath: str) -> None:
        """Load state from disk."""
        self.state.load_state(filepath)
    
    # ==================== COMMUNICATION COMPONENT IMPLEMENTATION ====================
    
    async def start_communication(self) -> None:
        """Start communication interfaces."""
        await self.communication.start_communication()
    
    async def stop_communication(self) -> None:
        """Stop communication interfaces."""
        await self.communication.stop_communication()
    
    async def publish_prediction(self, prediction: Dict[str, Any]) -> None:
        """Publish prediction to channels."""
        await self.communication.publish_prediction(prediction)
    
    # ==================== ALERTS COMPONENT IMPLEMENTATION ====================
    
    async def handle_alerts(self, logic_output: Dict[str, Any]) -> None:
        """Handle alerts based on logic output."""
        await self.alerts.handle_alerts(logic_output)
    
    # ==================== MAIN PROCESSING LOOP ====================
    
    async def _process_sensor_data(self, sensor_data: Dict[str, Any]) -> None:
        """Process incoming sensor data."""
        try:
            logger.debug(f"Processing sensor data: {sensor_data}")
            
            # Step 1: Preprocess
            preprocessed = self.preprocess(sensor_data)
            if preprocessed is None:
                logger.debug("Insufficient data for prediction")
                return
            
            # Step 2: Predict
            prediction = self.predict(preprocessed)
            logger.info(f"Prediction: Consumption={prediction.get('consumption_kwh')} kWh, "
                       f"Efficiency={prediction.get('efficiency_score')}%")
            
            # Step 3: Apply logic
            logic_output = self.apply_logic(prediction)
            logger.info(f"Logic output: {logic_output.get('alert_level')} - "
                       f"{logic_output.get('action')}")
            
            # Step 4: Update state
            self.update_state(prediction, logic_output)
            
            # Step 5: Publish prediction
            combined = {**prediction, **logic_output}
            await self.publish_prediction(combined)
            
            # Step 6: Handle alerts
            await self.handle_alerts(logic_output)
            
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}", exc_info=True)
            self.state.update({}, {"alert_level": "ERROR"}, success=False)
    
    async def initialize(self) -> None:
        """Initialize agent components."""
        await super().initialize()
        
        # Load model
        model_path = self.config.get('model', {}).get('path')
        if model_path:
            self.load_model(model_path)
        
        # Load state if exists
        state_path = self.config.get('state', {}).get('checkpoint_path')
        if state_path:
            self.load_state(state_path)
        
        # Start checkpointing
        await self.state.start_checkpointing()
        
        logger.info("Energy Agent initialized successfully")
    
    async def stop(self) -> None:
        """Stop agent gracefully."""
        await self.state.stop_checkpointing()
        
        state_path = self.config.get('state', {}).get('checkpoint_path')
        if state_path:
            self.save_state(state_path)
        
        await super().stop()


async def main():
    """Main entry point."""
    # Load configuration
    agents_dir = os.path.dirname(os.path.dirname(__file__))
    config_dir = os.path.join(agents_dir, 'config')
    config = load_agent_config('energy_agent', config_dir)
    
    # Make model paths relative to Backend root or energy directory
    energy_dir = os.path.dirname(__file__)
    backend_root = os.path.dirname(os.path.dirname(energy_dir))
    
    if 'model' in config:
        model_path = config['model'].get('path', 'artifacts/model.pkl')
        if not os.path.isabs(model_path):
            full_path = os.path.join(energy_dir, model_path)
            if not os.path.exists(full_path):
                full_path = os.path.join(backend_root, model_path.replace('../', ''))
            config['model']['path'] = full_path
        
        anomaly_path = config['model'].get('anomaly_model_path')
        if anomaly_path and not os.path.isabs(anomaly_path):
            full_path = os.path.join(energy_dir, anomaly_path)
            if not os.path.exists(full_path):
                full_path = os.path.join(backend_root, anomaly_path.replace('../', ''))
            config['model']['anomaly_model_path'] = full_path
    
    # Make state path relative to energy directory
    if 'state' in config:
        state_path = config['state'].get('checkpoint_path', 'state/energy_agent_state.json')
        if not os.path.isabs(state_path):
            state_dir = os.path.join(energy_dir, 'state')
            os.makedirs(state_dir, exist_ok=True)
            config['state']['checkpoint_path'] = os.path.join(state_dir, 'energy_agent_state.json')
    
    # Override MQTT broker from environment if set
    if 'MQTT_BROKER' in os.environ:
        config['communication']['mqtt']['broker'] = os.environ['MQTT_BROKER']
    if 'MQTT_PORT' in os.environ:
        config['communication']['mqtt']['port'] = int(os.environ['MQTT_PORT'])
    
    # Create agent
    agent = EnergyAgent(config)
    
    # Setup signal handlers
    shutdown_event = asyncio.Event()
    
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        shutdown_event.set()
    
    if sys.platform != 'win32':
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await agent.start()
        logger.info("Energy Agent started. Press Ctrl+C to stop.")
        
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
        logger.info("Energy Agent stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")

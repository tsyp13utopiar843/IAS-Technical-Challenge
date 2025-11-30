"""
PM Agent Main Orchestrator
Predictive Maintenance Agent - Main entry point and orchestrator.
"""
import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agents.base_agent import BaseAgent
from agents.utils.config_loader import load_agent_config
from agents.maint.model import PMModel
from agents.maint.logic import PMLogic
from agents.maint.state import PMState
from agents.maint.communication import PMCommunication
from agents.maint.alerts import PMAlerts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("PMAgent")


class PMAgent(BaseAgent):
    """
    Predictive Maintenance Agent.
    
    Monitors equipment health using LSTM models, predicts RUL (Remaining Useful Life),
    and triggers maintenance alerts based on business rules.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize PM Agent."""
        agent_id = config.get('agent', {}).get('id', 'pm_agent')
        super().__init__(agent_id, config)
        
        # Initialize components
        self._init_components()
        
        logger.info(f"PM Agent initialized: {agent_id}")
    
    def _init_components(self) -> None:
        """Initialize all 5 components."""
        # Model component
        model_config = self.config.get('model', {})
        self.model = PMModel(
            model_path=model_config.get('path', 'artifacts/model.pkl'),
            scaler_path=model_config.get('scaler_path', 'artifacts/scaler.pkl'),
            sequence_length=model_config.get('sequence_length', 60),
            num_features=model_config.get('num_features', 6),
            label_encoder_path=model_config.get('label_encoder_path')
        )
        
        # Logic component
        logic_config = self.config.get('logic', {})
        self.logic = PMLogic(logic_config.get('thresholds', {}))
        
        # State component
        state_config = self.config.get('state', {})
        self.state = PMState(
            agent_id=self.agent_id,
            buffer_size=state_config.get('buffer_size', 100),
            checkpoint_interval=state_config.get('checkpoint_interval', 300),
            checkpoint_path=state_config.get('checkpoint_path', 'state/pm_agent_state.json')
        )
        
        # Communication component
        comm_config = self.config.get('communication', {})
        self.communication = PMCommunication(
            agent_id=self.agent_id,
            config=comm_config,
            prediction_callback=self._process_sensor_data
        )
        self.communication.state = self.state
        self.communication.model = self.model
        
        # Alerts component
        alerts_config = self.config.get('alerts', {})
        self.alerts = PMAlerts(
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
        """
        Process incoming sensor data.
        
        This is called by the communication component when MQTT messages arrive.
        """
        try:
            logger.debug(f"Processing sensor data: {sensor_data}")
            
            # Step 1: Preprocess
            preprocessed = self.preprocess(sensor_data)
            if preprocessed is None:
                logger.debug("Insufficient data for prediction")
                return
            
            # Step 2: Predict
            prediction = self.predict(preprocessed)
            logger.info(f"Prediction: RUL={prediction.get('rul_hours')}h, "
                       f"Health={prediction.get('health_score')}%")
            
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
        
        logger.info("PM Agent initialized successfully")
    
    async def stop(self) -> None:
        """Stop agent gracefully."""
        # Stop checkpointing
        await self.state.stop_checkpointing()
        
        # Save state
        state_path = self.config.get('state', {}).get('checkpoint_path')
        if state_path:
            self.save_state(state_path)
        
        await super().stop()


async def main():
    """Main entry point."""
    # Load configuration
    # Config directory is relative to agents/ directory
    agents_dir = os.path.dirname(os.path.dirname(__file__))
    config_dir = os.path.join(agents_dir, 'config')
    config = load_agent_config('pm_agent', config_dir)
    
    # Check for Hugging Face model repository in environment
    hf_model_repo = os.getenv('HF_MODEL_REPO')
    
    if hf_model_repo:
        logger.info(f"Using Hugging Face model repository: {hf_model_repo}")
        # Override model path with HF repo
        if 'model' not in config:
            config['model'] = {}
        config['model']['path'] = f"hf://{hf_model_repo}"
        # Scaler and label encoder will be loaded from HF as well
        config['model']['scaler_path'] = f"hf://{hf_model_repo}"
        if 'label_encoder_path' in config.get('model', {}):
            config['model']['label_encoder_path'] = f"hf://{hf_model_repo}"
    else:
        logger.info("No HF_MODEL_REPO set, using local model files")
        # Make model paths relative to Backend root or maint directory
        maint_dir = os.path.dirname(__file__)
        backend_root = os.path.dirname(os.path.dirname(maint_dir))
        
        if 'model' in config:
            model_path = config['model'].get('path', 'artifacts/model.pkl')
            if not os.path.isabs(model_path):
                # Try relative to maint directory first
                full_path = os.path.join(maint_dir, model_path)
                if not os.path.exists(full_path):
                    # Try relative to Backend root (remove ../ prefix if present)
                    full_path = os.path.join(backend_root, model_path.replace('../', ''))
                config['model']['path'] = full_path
            
            scaler_path = config['model'].get('scaler_path', 'artifacts/scaler.pkl')
            if scaler_path and not os.path.isabs(scaler_path):
                full_path = os.path.join(maint_dir, scaler_path)
                if not os.path.exists(full_path):
                    full_path = os.path.join(backend_root, scaler_path.replace('../', ''))
                config['model']['scaler_path'] = full_path
            
            label_encoder_path = config['model'].get('label_encoder_path')
            if label_encoder_path and not os.path.isabs(label_encoder_path):
                full_path = os.path.join(maint_dir, label_encoder_path)
                if not os.path.exists(full_path):
                    full_path = os.path.join(backend_root, label_encoder_path.replace('../', ''))
                config['model']['label_encoder_path'] = full_path
    
    # Make state path relative to maint directory
    if 'state' in config:
        state_path = config['state'].get('checkpoint_path', 'state/pm_agent_state.json')
        if not os.path.isabs(state_path):
            # Create state directory if needed
            state_dir = os.path.join(maint_dir, 'state')
            os.makedirs(state_dir, exist_ok=True)
            config['state']['checkpoint_path'] = os.path.join(state_dir, 'pm_agent_state.json')
    
    # Override MQTT broker from environment if set
    if 'MQTT_BROKER' in os.environ:
        config['communication']['mqtt']['broker'] = os.environ['MQTT_BROKER']
    if 'MQTT_PORT' in os.environ:
        config['communication']['mqtt']['port'] = int(os.environ['MQTT_PORT'])
    
    # Create agent
    agent = PMAgent(config)
    
    # Setup signal handlers
    shutdown_event = asyncio.Event()
    
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        shutdown_event.set()
    
    if sys.platform != 'win32':
        # Signal handlers work better on Unix systems
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start agent
        await agent.start()
        logger.info("PM Agent started. Press Ctrl+C to stop.")
        
        # Keep running until shutdown signal
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
        logger.info("PM Agent stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")

"""
Backlog Agent Main Orchestrator
Backlog Generation Agent - Main entry point and orchestrator.
"""
import asyncio
import logging
import signal
import sys
import os
from typing import Dict, Any
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent
from agents.utils.config_loader import load_agent_config
from agents.backlog.model import BacklogModel
from agents.backlog.logic import BacklogLogic
from agents.backlog.state import BacklogState
from agents.backlog.communication import BacklogCommunication
from agents.backlog.alerts import BacklogAlerts

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BacklogAgent")


class BacklogAgent(BaseAgent):
    """
    Backlog Generation Agent.
    
    Collects violations and anomalies from all monitoring agents during 8-hour shifts
    and generates comprehensive shift backlogs using GEMINI API via LangChain.
    """
    
    def __init__(self, config: Dict[str, Any]):
        agent_id = config.get('agent', {}).get('id', 'backlog_agent')
        super().__init__(agent_id, config)
        self._init_components()
        logger.info(f"Backlog Agent initialized: {agent_id}")
    
    def _init_components(self) -> None:
        # Model component (GEMINI + LangChain)
        model_config = self.config.get('model', {})
        self.model = BacklogModel(
            api_key=model_config.get('api_key') or os.getenv('GEMINI_API_KEY'),
            model_name=model_config.get('model_name', 'gemini-pro')
        )
        
        # Logic component
        logic_config = self.config.get('logic', {})
        self.logic = BacklogLogic(
            shift_duration_hours=logic_config.get('shift_duration_hours', 8)
        )
        
        # State component
        state_config = self.config.get('state', {})
        self.state = BacklogState(
            agent_id=self.agent_id,
            shift_duration_hours=logic_config.get('shift_duration_hours', 8),
            checkpoint_interval=state_config.get('checkpoint_interval', 300),
            checkpoint_path=state_config.get('checkpoint_path', 'state/backlog_agent_state.json')
        )
        
        # Communication component
        comm_config = self.config.get('communication', {})
        self.communication = BacklogCommunication(
            agent_id=self.agent_id,
            config=comm_config,
            event_callback=self._process_event
        )
        self.communication.state = self.state
        
        # Alerts component
        alerts_config = self.config.get('alerts', {})
        self.alerts = BacklogAlerts(
            agent_id=self.agent_id,
            config=alerts_config,
            mqtt_client=self.communication.mqtt_client
        )
        
        # Shift monitoring task
        self._shift_monitor_task: asyncio.Task = None
        
        logger.info("All components initialized")
    
    def load_model(self, model_path: str) -> None:
        """Load model (not applicable for LLM-based model)."""
        pass
    
    def preprocess(self, raw_data: Any) -> Any:
        """Preprocess raw data (not applicable)."""
        return raw_data
    
    def predict(self, preprocessed_data: Any) -> Dict[str, Any]:
        """Generate backlog from shift data."""
        return self.model.generate_backlog(preprocessed_data)
    
    def apply_logic(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules to prediction (backlog)."""
        # For backlog agent, logic is applied to shift_data in _monitor_shifts
        # This method is required by BaseAgent interface
        return {"shift_status": "NORMAL", "priority": 4}
    
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
    
    async def start_communication(self) -> None:
        """Start communication interfaces."""
        await self.communication.start_communication()
    
    async def stop_communication(self) -> None:
        """Stop communication interfaces."""
        await self.communication.stop_communication()
    
    async def publish_prediction(self, prediction: Dict[str, Any]) -> None:
        """Publish backlog to channels."""
        await self.communication.publish_backlog(prediction)
    
    async def handle_alerts(self, logic_output: Dict[str, Any]) -> None:
        """Handle alerts (not applicable for backlog agent)."""
        pass
    
    async def _process_event(self, event: Dict[str, Any]) -> None:
        """
        Process incoming alert event from other agents.
        
        Args:
            event: Alert event dictionary
        """
        try:
            # Add event to current shift collection
            self.state.add_event(event)
            logger.debug(f"Event collected: {event.get('agent_id')} - {event.get('alert_level')}")
        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)
    
    async def _monitor_shifts(self) -> None:
        """Monitor shift completion and generate backlogs."""
        logger.info("Shift monitoring started")
        
        while self._running:
            try:
                current_time = datetime.utcnow()
                shift_start = self.state.get_current_shift_start()
                
                # Check if shift is complete
                if self.logic.is_shift_complete(shift_start, current_time):
                    logger.info("Shift complete! Generating backlog...")
                    
                    # Get all events from completed shift
                    events = self.state.get_current_shift_events()
                    shift_end = current_time
                    
                    # Aggregate shift data
                    shift_data = self.logic.aggregate_shift_data(events, shift_start, shift_end)
                    
                    # Generate backlog using GEMINI
                    backlog = self.predict(shift_data)
                    
                    # Apply logic to shift data
                    logic_output = self.logic.apply_logic(shift_data)
                    
                    # Update state
                    self.update_state(backlog, logic_output)
                    
                    # Record backlog
                    self.state.record_backlog(backlog)
                    
                    # Save backlog to file
                    backlog_dir = self.config.get('state', {}).get('backlog_dir', 'backlogs')
                    self.state.save_backlog(backlog, backlog_dir)
                    
                    # Publish backlog
                    await self.publish_prediction(backlog)
                    
                    # Send alert if needed
                    await self.alerts.handle_backlog_generated(backlog)
                    
                    logger.info(f"Backlog generated: {backlog.get('backlog_id')} "
                               f"({backlog.get('total_violations')} violations, "
                               f"{backlog.get('total_anomalies')} anomalies)")
                    
                    # Start new shift
                    self.state.start_new_shift()
                
                # Check every minute
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in shift monitoring: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    async def initialize(self) -> None:
        """Initialize agent components."""
        await super().initialize()
        
        # Load state if exists
        state_path = self.config.get('state', {}).get('checkpoint_path')
        if state_path:
            self.load_state(state_path)
        
        # Start checkpointing
        await self.state.start_checkpointing()
        
        # Start shift monitoring
        self._shift_monitor_task = asyncio.create_task(self._monitor_shifts())
        
        logger.info("Backlog Agent initialized successfully")
    
    async def stop(self) -> None:
        """Stop agent gracefully."""
        # Stop shift monitoring
        if self._shift_monitor_task:
            self._shift_monitor_task.cancel()
            try:
                await self._shift_monitor_task
            except asyncio.CancelledError:
                pass
        
        await self.state.stop_checkpointing()
        
        state_path = self.config.get('state', {}).get('checkpoint_path')
        if state_path:
            self.save_state(state_path)
        
        await super().stop()


async def main():
    """Main entry point."""
    agents_dir = os.path.dirname(os.path.dirname(__file__))
    config_dir = os.path.join(agents_dir, 'config')
    config = load_agent_config('backlog_agent', config_dir)
    
    backlog_dir = os.path.dirname(__file__)
    
    # Make state path relative to backlog directory
    if 'state' in config:
        state_path = config['state'].get('checkpoint_path', 'state/backlog_agent_state.json')
        if not os.path.isabs(state_path):
            state_dir = os.path.join(backlog_dir, 'state')
            os.makedirs(state_dir, exist_ok=True)
            config['state']['checkpoint_path'] = os.path.join(state_dir, 'backlog_agent_state.json')
        
        # Make backlog directory relative
        backlog_save_dir = config['state'].get('backlog_dir', 'backlogs')
        if not os.path.isabs(backlog_save_dir):
            config['state']['backlog_dir'] = os.path.join(backlog_dir, backlog_save_dir)
    
    # Override MQTT broker from environment if set
    if 'MQTT_BROKER' in os.environ:
        config['communication']['mqtt']['broker'] = os.environ['MQTT_BROKER']
    if 'MQTT_PORT' in os.environ:
        config['communication']['mqtt']['port'] = int(os.environ['MQTT_PORT'])
    
    # Create agent
    agent = BacklogAgent(config)
    
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
        logger.info("Backlog Agent started. Press Ctrl+C to stop.")
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
        logger.info("Backlog Agent stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutdown complete")


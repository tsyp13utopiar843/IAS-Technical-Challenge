"""
Cyber Agent State Component
Manages agent state, prediction history, and persistence.
"""
from typing import Dict, Any, Optional
import logging
import asyncio
from datetime import datetime
import os

from agents.utils.state_manager import StateManager

logger = logging.getLogger("CyberAgent.State")


class CyberState:
    """Cyber Threat Detection State Component."""
    
    def __init__(self, agent_id: str, buffer_size: int = 100, checkpoint_interval: int = 300,
                 checkpoint_path: str = "state/cyber_agent_state.json"):
        """Initialize state component."""
        self.agent_id = agent_id
        self.checkpoint_path = checkpoint_path
        self.checkpoint_interval = checkpoint_interval
        
        self.state_manager = StateManager(agent_id, buffer_size, checkpoint_interval)
        self.state_manager.status = "initializing"
        
        # Cyber-specific state
        self.state_manager.custom_state = {
            "last_alert_level": "NORMAL",
            "blocked_ips": [],
            "threat_count": 0,
            "last_threat_time": None
        }
        
        self._checkpoint_task: Optional[asyncio.Task] = None
        logger.info(f"Initialized Cyber State (buffer_size={buffer_size}, checkpoint_interval={checkpoint_interval}s)")
    
    def update(self, prediction: Dict[str, Any], logic_output: Dict[str, Any], success: bool = True) -> None:
        """Update state with new prediction and logic output."""
        combined = {**prediction, **logic_output, "timestamp": datetime.utcnow().isoformat()}
        self.state_manager.update(combined, success)
        
        alert_level = logic_output.get('alert_level', 'NORMAL')
        self.state_manager.custom_state['last_alert_level'] = alert_level
        
        if alert_level in ['WARNING', 'CRITICAL']:
            self.state_manager.custom_state['threat_count'] += 1
            self.state_manager.custom_state['last_threat_time'] = datetime.utcnow().isoformat()
        
        if alert_level == 'CRITICAL':
            self.state_manager.status = "critical"
        elif alert_level == 'WARNING':
            self.state_manager.status = "warning"
        else:
            self.state_manager.status = "active"
        
        logger.debug(f"State updated: alert_level={alert_level}, status={self.state_manager.status}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current agent state."""
        state = self.state_manager.to_dict()
        state['status'] = self.state_manager.status
        return state
    
    def save_state(self, filepath: Optional[str] = None) -> None:
        """Persist agent state to disk."""
        try:
            path = filepath or self.checkpoint_path
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.state_manager.save(path)
            logger.debug(f"State saved to {path}")
        except Exception as e:
            logger.error(f"Failed to save state: {e}", exc_info=True)
    
    def load_state(self, filepath: Optional[str] = None) -> None:
        """Load agent state from disk."""
        try:
            path = filepath or self.checkpoint_path
            self.state_manager.load(path)
            logger.info(f"State loaded from {path}")
        except Exception as e:
            logger.warning(f"Failed to load state: {e}")
    
    async def start_checkpointing(self) -> None:
        """Start automatic checkpointing task."""
        if self._checkpoint_task is not None:
            return
        
        async def checkpoint_loop():
            while True:
                try:
                    await asyncio.sleep(self.checkpoint_interval)
                    self.save_state()
                    logger.debug("Automatic checkpoint saved")
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Checkpoint error: {e}", exc_info=True)
        
        self._checkpoint_task = asyncio.create_task(checkpoint_loop())
        logger.info("Checkpointing started")
    
    async def stop_checkpointing(self) -> None:
        """Stop automatic checkpointing task."""
        if self._checkpoint_task:
            self._checkpoint_task.cancel()
            try:
                await self._checkpoint_task
            except asyncio.CancelledError:
                pass
            self._checkpoint_task = None
            logger.info("Checkpointing stopped")
    
    def reset(self) -> None:
        """Reset state to initial values."""
        self.state_manager.reset()
        self.state_manager.custom_state = {
            "last_alert_level": "NORMAL",
            "blocked_ips": [],
            "threat_count": 0,
            "last_threat_time": None
        }
        logger.info("State reset")


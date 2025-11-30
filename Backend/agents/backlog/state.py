"""
Backlog Agent State Component
Manages agent state, shift tracking, and backlog storage.
"""
from typing import Dict, Any, Optional, List
import logging
import asyncio
from datetime import datetime, timedelta
import os
import json

from agents.utils.state_manager import StateManager

logger = logging.getLogger("BacklogAgent.State")


class BacklogState:
    """
    Backlog Generation State Component.
    
    Manages shift tracking, event collection, and backlog storage.
    """
    
    def __init__(self, agent_id: str, shift_duration_hours: int = 8,
                 checkpoint_interval: int = 300,
                 checkpoint_path: str = "state/backlog_agent_state.json"):
        """
        Initialize state component.
        
        Args:
            agent_id: Agent identifier
            shift_duration_hours: Duration of each shift in hours
            checkpoint_interval: Seconds between automatic checkpoints
            checkpoint_path: Path to state checkpoint file
        """
        self.agent_id = agent_id
        self.checkpoint_path = checkpoint_path
        self.checkpoint_interval = checkpoint_interval
        self.shift_duration_hours = shift_duration_hours
        
        self.state_manager = StateManager(agent_id, buffer_size=1000, checkpoint_interval=checkpoint_interval)
        self.state_manager.status = "initializing"
        
        # Backlog-specific state
        self.state_manager.custom_state = {
            "current_shift_start": datetime.utcnow().isoformat(),
            "shift_events": [],  # Events collected during current shift
            "backlogs_generated": 0,
            "last_backlog_time": None,
            "backlog_history": []  # List of generated backlog IDs
        }
        
        self._checkpoint_task: Optional[asyncio.Task] = None
        logger.info(f"Initialized Backlog State (shift_duration={shift_duration_hours}h, "
                   f"checkpoint_interval={checkpoint_interval}s)")
    
    def add_event(self, event: Dict[str, Any]) -> None:
        """
        Add event to current shift collection.
        
        Args:
            event: Event dictionary (violation or anomaly)
        """
        # Add timestamp if not present
        if 'timestamp' not in event:
            event['timestamp'] = datetime.utcnow().isoformat()
        
        self.state_manager.custom_state['shift_events'].append(event)
        logger.debug(f"Event added to shift collection: {event.get('agent_id')} - {event.get('alert_level')}")
    
    def get_current_shift_events(self) -> List[Dict[str, Any]]:
        """Get all events collected during current shift."""
        return self.state_manager.custom_state.get('shift_events', [])
    
    def start_new_shift(self) -> datetime:
        """
        Start a new shift.
        
        Returns:
            New shift start timestamp
        """
        new_shift_start = datetime.utcnow()
        self.state_manager.custom_state['current_shift_start'] = new_shift_start.isoformat()
        self.state_manager.custom_state['shift_events'] = []
        logger.info(f"New shift started: {new_shift_start.isoformat()}")
        return new_shift_start
    
    def get_current_shift_start(self) -> datetime:
        """Get current shift start timestamp."""
        shift_start_str = self.state_manager.custom_state.get('current_shift_start')
        if shift_start_str:
            return datetime.fromisoformat(shift_start_str)
        return datetime.utcnow()
    
    def record_backlog(self, backlog: Dict[str, Any]) -> None:
        """
        Record generated backlog.
        
        Args:
            backlog: Generated backlog dictionary
        """
        backlog_id = backlog.get('backlog_id', 'unknown')
        self.state_manager.custom_state['backlogs_generated'] += 1
        self.state_manager.custom_state['last_backlog_time'] = datetime.utcnow().isoformat()
        
        # Add to history (keep last 10)
        history = self.state_manager.custom_state.get('backlog_history', [])
        history.append({
            'backlog_id': backlog_id,
            'generated_at': backlog.get('generated_at'),
            'shift_period': backlog.get('shift_period', {}),
            'total_events': backlog.get('total_violations', 0) + backlog.get('total_anomalies', 0)
        })
        self.state_manager.custom_state['backlog_history'] = history[-10:]  # Keep last 10
        
        logger.info(f"Backlog recorded: {backlog_id}")
    
    def update(self, prediction: Dict[str, Any], logic_output: Dict[str, Any], success: bool = True) -> None:
        """Update state with new prediction and logic output."""
        combined = {**prediction, **logic_output, "timestamp": datetime.utcnow().isoformat()}
        self.state_manager.update(combined, success)
        
        shift_status = logic_output.get('shift_status', 'NORMAL')
        if shift_status == 'CRITICAL':
            self.state_manager.status = "critical"
        elif shift_status == 'WARNING':
            self.state_manager.status = "warning"
        else:
            self.state_manager.status = "active"
    
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
    
    def save_backlog(self, backlog: Dict[str, Any], backlog_dir: str = "backlogs") -> str:
        """
        Save backlog to file.
        
        Args:
            backlog: Backlog dictionary
            backlog_dir: Directory to save backlogs
        
        Returns:
            Path to saved backlog file
        """
        try:
            os.makedirs(backlog_dir, exist_ok=True)
            backlog_id = backlog.get('backlog_id', f"backlog_{datetime.utcnow().isoformat()}")
            filename = f"{backlog_id}.json"
            filepath = os.path.join(backlog_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(backlog, f, indent=2)
            
            logger.info(f"Backlog saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to save backlog: {e}", exc_info=True)
            return ""
    
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
            "current_shift_start": datetime.utcnow().isoformat(),
            "shift_events": [],
            "backlogs_generated": 0,
            "last_backlog_time": None,
            "backlog_history": []
        }
        logger.info("State reset")


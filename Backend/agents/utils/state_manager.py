"""
State Manager Base Class
Handles state persistence, history tracking, and metrics.
"""
import json
import os
from typing import Dict, Any, Optional, Deque
from collections import deque
from datetime import datetime
import logging

logger = logging.getLogger("StateManager")


class StateManager:
    """Base class for agent state management."""
    
    def __init__(self, agent_id: str, buffer_size: int = 100, checkpoint_interval: int = 300):
        """
        Initialize state manager.
        
        Args:
            agent_id: Agent identifier
            buffer_size: Size of prediction history buffer
            checkpoint_interval: Seconds between automatic checkpoints
        """
        self.agent_id = agent_id
        self.buffer_size = buffer_size
        self.checkpoint_interval = checkpoint_interval
        
        # Core state
        self.status = "initializing"
        self.uptime_start = datetime.utcnow()
        self.predictions_made = 0
        self.errors = 0
        
        # Prediction history
        self.prediction_history: Deque[Dict[str, Any]] = deque(maxlen=buffer_size)
        self.last_prediction: Optional[Dict[str, Any]] = None
        
        # Metrics
        self.metrics = {
            "total_predictions": 0,
            "successful_predictions": 0,
            "failed_predictions": 0,
            "average_latency_ms": 0.0
        }
        
        # Custom state (agent-specific)
        self.custom_state: Dict[str, Any] = {}
    
    def update(self, prediction: Dict[str, Any], success: bool = True) -> None:
        """
        Update state with new prediction.
        
        Args:
            prediction: Prediction data
            success: Whether prediction was successful
        """
        self.predictions_made += 1
        self.metrics["total_predictions"] += 1
        
        if success:
            self.metrics["successful_predictions"] += 1
            self.last_prediction = prediction
            self.prediction_history.append(prediction)
        else:
            self.metrics["failed_predictions"] += 1
            self.errors += 1
    
    def get_uptime(self) -> float:
        """Get agent uptime in seconds."""
        return (datetime.utcnow() - self.uptime_start).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert state to dictionary for serialization.
        
        Returns:
            State dictionary
        """
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "uptime": self.get_uptime(),
            "predictions_made": self.predictions_made,
            "errors": self.errors,
            "last_prediction": self.last_prediction,
            "prediction_history": list(self.prediction_history),
            "metrics": self.metrics,
            "custom_state": self.custom_state,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def from_dict(self, state_dict: Dict[str, Any]) -> None:
        """
        Load state from dictionary.
        
        Args:
            state_dict: State dictionary
        """
        self.agent_id = state_dict.get("agent_id", self.agent_id)
        self.status = state_dict.get("status", "unknown")
        self.predictions_made = state_dict.get("predictions_made", 0)
        self.errors = state_dict.get("errors", 0)
        self.last_prediction = state_dict.get("last_prediction")
        
        # Restore history
        history = state_dict.get("prediction_history", [])
        self.prediction_history = deque(history[-self.buffer_size:], maxlen=self.buffer_size)
        
        self.metrics = state_dict.get("metrics", self.metrics)
        self.custom_state = state_dict.get("custom_state", {})
    
    def save(self, filepath: str) -> None:
        """
        Save state to JSON file.
        
        Args:
            filepath: Path to save file
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        logger.info(f"State saved to {filepath}")
    
    def load(self, filepath: str) -> None:
        """
        Load state from JSON file.
        
        Args:
            filepath: Path to state file
        """
        if not os.path.exists(filepath):
            logger.warning(f"State file not found: {filepath}")
            return
        
        with open(filepath, 'r') as f:
            state_dict = json.load(f)
        
        self.from_dict(state_dict)
        logger.info(f"State loaded from {filepath}")
    
    def reset(self) -> None:
        """Reset state to initial values."""
        self.status = "active"
        self.uptime_start = datetime.utcnow()
        self.predictions_made = 0
        self.errors = 0
        self.prediction_history.clear()
        self.last_prediction = None
        self.metrics = {
            "total_predictions": 0,
            "successful_predictions": 0,
            "failed_predictions": 0,
            "average_latency_ms": 0.0
        }
        self.custom_state = {}
        logger.info(f"State reset for {self.agent_id}")

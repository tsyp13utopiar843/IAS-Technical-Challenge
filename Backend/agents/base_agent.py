"""
Base Agent Abstract Class
Defines the standard interface and lifecycle for all AI agents in the system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from collections import deque
import logging
import asyncio
from datetime import datetime


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    Each agent must implement 5 core components:
    1. Model - ML/DL model loading and inference
    2. Logic - Business rules and decision making
    3. State - State management and persistence
    4. Communication - MQTT/API/WebSocket interfaces
    5. Alerts - Alert routing and action execution
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any]):
        """
        Initialize base agent.
        
        Args:
            agent_id: Unique identifier for this agent
            config: Configuration dictionary loaded from YAML
        """
        self.agent_id = agent_id
        self.config = config
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        
        # Component references (to be initialized by subclasses)
        self.model = None
        self.logic = None
        self.state = None
        self.communication = None
        self.alerts = None
        
        # Runtime state
        self._running = False
        self._task = None
        
        self.logger.info(f"Initialized {agent_id}")
    
    # ==================== MODEL COMPONENT ====================
    
    @abstractmethod
    def load_model(self, model_path: str) -> None:
        """
        Load the trained ML/DL model from disk.
        
        Args:
            model_path: Path to the model file (.h5, .pkl, .keras)
        
        Raises:
            FileNotFoundError: If model file not found
            ValueError: If model format is invalid
        """
        pass
    
    @abstractmethod
    def preprocess(self, raw_data: Any) -> Any:
        """
        Preprocess raw input data for model inference.
        
        Args:
            raw_data: Raw sensor data or input
        
        Returns:
            Preprocessed data ready for model
        """
        pass
    
    @abstractmethod
    def predict(self, preprocessed_data: Any) -> Dict[str, Any]:
        """
        Run model inference on preprocessed data.
        
        Args:
            preprocessed_data: Data after preprocessing
        
        Returns:
            Dictionary containing prediction results
        """
        pass
    
    # ==================== LOGIC COMPONENT ====================
    
    @abstractmethod
    def apply_logic(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply business rules to model prediction.
        
        Args:
            prediction: Raw model prediction output
        
        Returns:
            Dictionary with alert_level, action, priority, etc.
        """
        pass
    
    # ==================== STATE COMPONENT ====================
    
    @abstractmethod
    def update_state(self, prediction: Dict[str, Any], logic_output: Dict[str, Any]) -> None:
        """
        Update agent state with new prediction and logic results.
        
        Args:
            prediction: Model prediction
            logic_output: Logic component output
        """
        pass
    
    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """
        Get current agent state.
        
        Returns:
            Dictionary containing current agent state
        """
        pass
    
    @abstractmethod
    def save_state(self, filepath: str) -> None:
        """
        Persist agent state to disk.
        
        Args:
            filepath: Path to save state file
        """
        pass
    
    @abstractmethod
    def load_state(self, filepath: str) -> None:
        """
        Load agent state from disk.
        
        Args:
            filepath: Path to state file
        """
        pass
    
    # ==================== COMMUNICATION COMPONENT ====================
    
    @abstractmethod
    async def start_communication(self) -> None:
        """
        Start communication interfaces (MQTT, API, WebSocket).
        """
        pass
    
    @abstractmethod
    async def stop_communication(self) -> None:
        """
        Stop communication interfaces gracefully.
        """
        pass
    
    @abstractmethod
    async def publish_prediction(self, prediction: Dict[str, Any]) -> None:
        """
        Publish prediction to configured channels.
        
        Args:
            prediction: Prediction to publish
        """
        pass
    
    # ==================== ALERTS COMPONENT ====================
    
    @abstractmethod
    async def handle_alerts(self, logic_output: Dict[str, Any]) -> None:
        """
        Trigger alerts and actions based on logic output.
        
        Args:
            logic_output: Output from logic component
        """
        pass
    
    # ==================== LIFECYCLE MANAGEMENT ====================
    
    async def initialize(self) -> None:
        """
        Initialize all agent components.
        Called before starting the agent.
        """
        self.logger.info(f"Initializing {self.agent_id}...")
        
        # Load model
        model_path = self.config.get('model', {}).get('path')
        if model_path:
            self.load_model(model_path)
            self.logger.info(f"Model loaded from {model_path}")
        
        # Initialize communication
        await self.start_communication()
        self.logger.info("Communication interfaces started")
        
        self.logger.info(f"{self.agent_id} initialized successfully")
    
    async def run(self) -> None:
        """
        Main agent loop.
        Continuously processes incoming data and generates predictions.
        """
        self._running = True
        self.logger.info(f"Starting {self.agent_id} main loop")
        
        try:
            while self._running:
                try:
                    # This is a placeholder - actual implementation depends on
                    # how each agent receives data (MQTT callback, queue, etc.)
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    self.logger.error(f"Error in agent loop: {e}", exc_info=True)
                    await asyncio.sleep(1)  # Back off on error
        
        except asyncio.CancelledError:
            self.logger.info("Agent loop cancelled")
        finally:
            self._running = False
    
    async def start(self) -> None:
        """
        Start the agent.
        """
        await self.initialize()
        self._task = asyncio.create_task(self.run())
        self.logger.info(f"{self.agent_id} started")
    
    async def stop(self) -> None:
        """
        Stop the agent gracefully.
        """
        self.logger.info(f"Stopping {self.agent_id}...")
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        await self.stop_communication()
        
        # Save state before shutdown
        state_path = self.config.get('state', {}).get('checkpoint_path', f'state/{self.agent_id}_state.json')
        try:
            self.save_state(state_path)
            self.logger.info(f"State saved to {state_path}")
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
        
        self.logger.info(f"{self.agent_id} stopped")
    
    async def restart(self) -> None:
        """
        Restart the agent.
        """
        self.logger.info(f"Restarting {self.agent_id}...")
        await self.stop()
        await asyncio.sleep(1)
        await self.start()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Get agent health status.
        
        Returns:
            Dictionary with health information
        """
        state = self.get_state()
        
        return {
            "agent_id": self.agent_id,
            "status": state.get('status', 'unknown'),
            "running": self._running,
            "model_loaded": self.model is not None,
            "uptime": state.get('uptime', 0),
            "predictions_made": state.get('predictions_made', 0),
            "last_prediction_time": state.get('last_prediction', {}).get('timestamp'),
            "errors": state.get('errors', 0)
        }

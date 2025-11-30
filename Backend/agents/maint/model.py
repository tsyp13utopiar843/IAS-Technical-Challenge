"""
PM Agent Model Component
Handles LSTM model loading, data preprocessing, and inference.
"""
import pickle
import numpy as np
from typing import Dict, Any, List, Optional
from collections import deque
import logging
from pathlib import Path

logger = logging.getLogger("PMAgent.Model")


class PMModel:
    """
    Predictive Maintenance Model Component.
    
    Loads LSTM model and StandardScaler, preprocesses sensor data into
    60-minute time windows, and runs inference.
    """
    
    def __init__(self, model_path: str, scaler_path: str, sequence_length: int = 60, num_features: int = 6,
                 label_encoder_path: Optional[str] = None):
        """
        Initialize model component.
        
        Args:
            model_path: Path to model pickle file (Random Forest pipeline)
            scaler_path: Path to StandardScaler pickle file
            sequence_length: Time window length (minutes)
            num_features: Number of input features
            label_encoder_path: Path to label encoder (optional)
        """
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.label_encoder_path = label_encoder_path
        self.sequence_length = sequence_length
        self.num_features = num_features
        
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.data_buffer: deque = deque(maxlen=sequence_length)
        
        logger.info(f"Initialized PM Model (sequence_length={sequence_length}, num_features={num_features})")
    
    def load_model(self) -> None:
        """Load Random Forest pipeline model and scaler from pickle files."""
        try:
            # Load model (Random Forest pipeline)
            if not Path(self.model_path).exists():
                logger.warning(f"Model file not found: {self.model_path}. Using mock model.")
                self.model = None
            else:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded Random Forest model from {self.model_path}")
            
            # Load scaler
            if not Path(self.scaler_path).exists():
                logger.warning(f"Scaler file not found: {self.scaler_path}. Using mock scaler.")
                self.scaler = None
            else:
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info(f"Loaded scaler from {self.scaler_path}")
            
            # Load label encoder if provided
            if self.label_encoder_path and Path(self.label_encoder_path).exists():
                with open(self.label_encoder_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                logger.info(f"Loaded label encoder from {self.label_encoder_path}")
                
        except Exception as e:
            logger.error(f"Failed to load model/scaler: {e}", exc_info=True)
            self.model = None
            self.scaler = None
            self.label_encoder = None
    
    def preprocess(self, raw_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Preprocess raw sensor data into model input format.
        
        Expected features: temperature, vibration, pressure, RPM, torque, tool_wear
        If features are missing, uses available data and fills missing with defaults.
        
        Args:
            raw_data: Dictionary with sensor readings
            
        Returns:
            Preprocessed array of shape (sequence_length, num_features) or None if insufficient data
        """
        try:
            # Extract features (handle various field names)
            features = self._extract_features(raw_data)
            
            # Add to buffer
            self.data_buffer.append(features)
            
            # Check if we have enough data
            if len(self.data_buffer) < self.sequence_length:
                logger.debug(f"Insufficient data: {len(self.data_buffer)}/{self.sequence_length}")
                return None
            
            # Convert buffer to array
            sequence = np.array(list(self.data_buffer))
            
            # Apply scaler if available
            if self.scaler is not None:
                sequence = self.scaler.transform(sequence)
            else:
                # Mock normalization if scaler not available
                logger.debug("Using mock normalization (scaler not available)")
                sequence = (sequence - sequence.mean(axis=0)) / (sequence.std(axis=0) + 1e-8)
            
            # Reshape for LSTM: (1, sequence_length, num_features)
            sequence = sequence.reshape(1, self.sequence_length, self.num_features)
            
            return sequence
            
        except Exception as e:
            logger.error(f"Preprocessing error: {e}", exc_info=True)
            return None
    
    def _extract_features(self, raw_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract 6 features from raw data.
        
        Handles various field name formats and fills missing features with defaults.
        """
        # Feature extraction with fallbacks
        temperature = float(raw_data.get('temperature', raw_data.get('Temperature_C', raw_data.get('temp', 50.0))))
        vibration = float(raw_data.get('vibration', raw_data.get('Vibration_Hz', raw_data.get('vib', 0.5))))
        pressure = float(raw_data.get('pressure', raw_data.get('Pressure_psi', raw_data.get('press', 100.0))))
        rpm = float(raw_data.get('rpm', raw_data.get('RPM', raw_data.get('speed', 1500.0))))
        torque = float(raw_data.get('torque', raw_data.get('Torque_Nm', raw_data.get('torq', 50.0))))
        tool_wear = float(raw_data.get('tool_wear', raw_data.get('Tool_Wear_mm', raw_data.get('wear', 0.0))))
        
        return np.array([temperature, vibration, pressure, rpm, torque, tool_wear])
    
    def predict(self, preprocessed_data: np.ndarray) -> Dict[str, Any]:
        """
        Run model inference on preprocessed data.
        
        Args:
            preprocessed_data: Preprocessed array of shape (1, sequence_length, num_features)
            
        Returns:
            Dictionary with prediction results:
            - rul_hours: Remaining Useful Life in hours
            - health_score: Health score (0-100)
            - failure_probability: Probability of failure (0-1)
            - confidence: Prediction confidence (0-1)
        """
        try:
            if self.model is None:
                # Mock prediction if model not available
                logger.debug("Using mock prediction (model not available)")
                return self._mock_predict(preprocessed_data)
            
            # Flatten sequence for Random Forest (RF expects 2D array)
            # Use the most recent sample or average of sequence
            if preprocessed_data.ndim == 3:
                # Take the last sample from the sequence
                features = preprocessed_data[0, -1, :].reshape(1, -1)
            else:
                features = preprocessed_data.reshape(1, -1)
            
            # Run Random Forest inference
            # The model might be a pipeline or just the RF model
            if hasattr(self.model, 'predict'):
                prediction = self.model.predict(features)
                # Get prediction probabilities if available
                if hasattr(self.model, 'predict_proba'):
                    proba = self.model.predict_proba(features)
                    failure_probability = float(proba[0][1]) if proba.shape[1] > 1 else 0.0
                else:
                    failure_probability = 0.5
            else:
                # If it's a pipeline, use it directly
                prediction = self.model.predict(features)
                failure_probability = 0.5
            
            # Handle different model output formats
            if isinstance(prediction, (list, tuple)):
                prediction = prediction[0]
            
            if isinstance(prediction, np.ndarray):
                if prediction.ndim > 1:
                    prediction = prediction[0]
                rul_raw = float(prediction[0]) if len(prediction) > 0 else 48.0
            else:
                rul_raw = float(prediction)
            
            # Convert RUL to hours (assuming model outputs in hours or days)
            # If model outputs days, multiply by 24
            rul_hours = rul_raw if rul_raw < 1000 else rul_raw * 24
            
            # Calculate health score (inverse of failure probability)
            # Higher RUL = higher health score
            health_score = min(100.0, max(0.0, (rul_hours / 168.0) * 100.0))  # 168h = 1 week
            
            # Use failure probability from model if available
            if failure_probability == 0.5:
                failure_probability = max(0.0, min(1.0, 1.0 - (health_score / 100.0)))
            
            # Confidence based on RUL range
            if rul_hours > 72:
                confidence = 0.85
            elif rul_hours > 24:
                confidence = 0.75
            else:
                confidence = 0.90  # Higher confidence for critical predictions
            
            return {
                "rul_hours": round(rul_hours, 2),
                "health_score": round(health_score, 2),
                "failure_probability": round(failure_probability, 3),
                "confidence": round(confidence, 2)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            # Return safe defaults on error
            return {
                "rul_hours": 48.0,
                "health_score": 50.0,
                "failure_probability": 0.5,
                "confidence": 0.0
            }
    
    def _mock_predict(self, preprocessed_data: np.ndarray) -> Dict[str, Any]:
        """
        Mock prediction when model is not available.
        Uses simple heuristics based on input features.
        """
        # Extract average values from sequence
        avg_features = preprocessed_data[0].mean(axis=0)
        temperature, vibration, pressure, rpm, torque, tool_wear = avg_features
        
        # Simple heuristic: high vibration + high temp = low RUL
        base_rul = 72.0  # hours
        
        if vibration > 0.8:
            base_rul -= 20
        if temperature > 80:
            base_rul -= 15
        if tool_wear > 0.5:
            base_rul -= 10
        
        rul_hours = max(0.0, base_rul)
        health_score = min(100.0, max(0.0, (rul_hours / 168.0) * 100.0))
        failure_probability = max(0.0, min(1.0, 1.0 - (health_score / 100.0)))
        confidence = 0.70
        
        return {
            "rul_hours": round(rul_hours, 2),
            "health_score": round(health_score, 2),
            "failure_probability": round(failure_probability, 3),
            "confidence": round(confidence, 2)
        }
    
    def reset_buffer(self) -> None:
        """Reset the data buffer."""
        self.data_buffer.clear()
        logger.debug("Data buffer reset")

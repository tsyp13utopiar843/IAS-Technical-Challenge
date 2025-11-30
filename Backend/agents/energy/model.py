"""
Energy Agent Model Component
Handles LSTM + Isolation Forest hybrid model for energy consumption prediction and anomaly detection.
"""
import pickle
import numpy as np
from typing import Dict, Any, List, Optional
from collections import deque
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("EnergyAgent.Model")


class EnergyModel:
    """
    Energy Consumption Optimization Model Component.
    
    Uses LSTM for consumption prediction and Isolation Forest for anomaly detection.
    Includes time feature engineering (cyclical hour/day encoding).
    """
    
    def __init__(self, model_path: str, anomaly_model_path: Optional[str] = None, 
                 sequence_length: int = 60, num_features: int = 5):
        """
        Initialize model component.
        
        Args:
            model_path: Path to LSTM model pickle file
            anomaly_model_path: Path to Isolation Forest model (optional)
            sequence_length: Time window length (minutes)
            num_features: Number of input features
        """
        self.model_path = model_path
        self.anomaly_model_path = anomaly_model_path
        self.sequence_length = sequence_length
        self.num_features = num_features
        
        self.model = None
        self.anomaly_model = None
        self.data_buffer: deque = deque(maxlen=sequence_length)
        
        # Baseline tracking (rolling 30-day average)
        self.baseline_consumption = 100.0  # kW default
        self.consumption_history: deque = deque(maxlen=43200)  # 30 days at 1-min intervals
        
        logger.info(f"Initialized Energy Model (sequence_length={sequence_length}, num_features={num_features})")
    
    def load_model(self) -> None:
        """Load LSTM (Keras) and Isolation Forest models."""
        try:
            # Resolve model path (handle relative paths from root)
            model_path = Path(self.model_path)
            if not model_path.is_absolute():
                if not model_path.exists():
                    # Try from Backend root
                    root_path = Path(__file__).parent.parent.parent / self.model_path
                    if root_path.exists():
                        model_path = root_path
            
            # Load LSTM model (Keras format)
            if not model_path.exists():
                logger.warning(f"Model file not found: {model_path}. Using mock model.")
                self.model = None
            else:
                if self.model_path.endswith('.keras') or self.model_path.endswith('.h5'):
                    try:
                        from tensorflow import keras
                        self.model = keras.models.load_model(str(model_path))
                        logger.info(f"Loaded Keras LSTM model from {model_path}")
                    except ImportError:
                        logger.error("TensorFlow/Keras not available. Install with: pip install tensorflow")
                        self.model = None
                    except Exception as e:
                        logger.error(f"Failed to load Keras model: {e}", exc_info=True)
                        self.model = None
                else:
                    # Try pickle format
                    with open(model_path, 'rb') as f:
                        self.model = pickle.load(f)
                    logger.info(f"Loaded pickle model from {model_path}")
            
            # Load Isolation Forest model (optional)
            if self.anomaly_model_path:
                anomaly_path = Path(self.anomaly_model_path)
                if not anomaly_path.is_absolute() and not anomaly_path.exists():
                    root_path = Path(__file__).parent.parent.parent / self.anomaly_model_path
                    if root_path.exists():
                        anomaly_path = root_path
                
                if anomaly_path.exists():
                    with open(anomaly_path, 'rb') as f:
                        self.anomaly_model = pickle.load(f)
                    logger.info(f"Loaded Isolation Forest model from {anomaly_path}")
                else:
                    logger.warning("Isolation Forest model not found. Anomaly detection will use heuristics.")
                    self.anomaly_model = None
            else:
                logger.info("No anomaly model path specified. Anomaly detection will use heuristics.")
                self.anomaly_model = None
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            self.model = None
            self.anomaly_model = None
    
    def preprocess(self, raw_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Preprocess raw sensor data with time feature engineering.
        
        Features: power_consumption, hour (cyclical), day_of_week (cyclical), 
                  temperature, production_load
        
        Args:
            raw_data: Dictionary with sensor readings
            
        Returns:
            Preprocessed array of shape (sequence_length, num_features) or None if insufficient data
        """
        try:
            # Extract features
            features = self._extract_features(raw_data)
            
            # Add to buffer
            self.data_buffer.append(features)
            
            # Update consumption history for baseline
            power = features[0]
            self.consumption_history.append(power)
            self._update_baseline()
            
            # Check if we have enough data
            if len(self.data_buffer) < self.sequence_length:
                logger.debug(f"Insufficient data: {len(self.data_buffer)}/{self.sequence_length}")
                return None
            
            # Convert buffer to array
            sequence = np.array(list(self.data_buffer))
            
            # Reshape for LSTM: (1, sequence_length, num_features)
            sequence = sequence.reshape(1, self.sequence_length, self.num_features)
            
            return sequence
            
        except Exception as e:
            logger.error(f"Preprocessing error: {e}", exc_info=True)
            return None
    
    def _extract_features(self, raw_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features with time encoding.
        
        Features:
        0. power_consumption (kW)
        1. hour_sin (cyclical encoding)
        2. hour_cos (cyclical encoding)
        3. temperature (C)
        4. production_load (normalized 0-1)
        """
        # Power consumption
        power = float(raw_data.get('current_load', raw_data.get('Power_Consumption_kW', 
                    raw_data.get('power', 100.0))))
        
        # Time features (cyclical encoding)
        now = datetime.utcnow()
        hour = now.hour
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        
        # Temperature
        temp = float(raw_data.get('temperature', raw_data.get('Temperature_C', 20.0)))
        
        # Production load (normalized)
        production = float(raw_data.get('production_load', raw_data.get('Production_Speed_units_per_hr', 100.0)))
        production_normalized = min(1.0, max(0.0, production / 200.0))  # Normalize to 0-1
        
        return np.array([power, hour_sin, hour_cos, temp, production_normalized])
    
    def _update_baseline(self) -> None:
        """Update baseline consumption (rolling 30-day average)."""
        if len(self.consumption_history) > 0:
            self.baseline_consumption = np.mean(list(self.consumption_history))
    
    def predict(self, preprocessed_data: np.ndarray) -> Dict[str, Any]:
        """
        Run model inference on preprocessed data.
        
        Args:
            preprocessed_data: Preprocessed array of shape (1, sequence_length, num_features)
            
        Returns:
            Dictionary with prediction results:
            - consumption_kwh: Predicted consumption in kWh
            - efficiency_score: Efficiency score (0-100)
            - anomaly_score: Anomaly score (0-1, higher = more anomalous)
            - is_anomaly: Boolean anomaly flag
            - baseline_consumption: Current baseline
            - confidence: Prediction confidence (0-1)
        """
        try:
            if self.model is None:
                # Mock prediction if model not available
                logger.debug("Using mock prediction (model not available)")
                return self._mock_predict(preprocessed_data)
            
            # Run LSTM inference (Keras or other format)
            if hasattr(self.model, 'predict'):
                # Keras model
                prediction = self.model.predict(preprocessed_data, verbose=0)
            else:
                # Other model types
                prediction = self.model.predict(preprocessed_data)
            
            # Handle different model output formats
            if isinstance(prediction, (list, tuple)):
                prediction = prediction[0]
            
            if isinstance(prediction, np.ndarray):
                if prediction.ndim > 1:
                    prediction = prediction[0]
                consumption_kw = float(prediction[0]) if len(prediction) > 0 else 100.0
            else:
                consumption_kw = float(prediction)
            
            # Convert to kWh (assuming prediction is per hour)
            consumption_kwh = consumption_kw  # Already in kWh if per hour
            
            # Detect anomalies
            anomaly_score, is_anomaly = self._detect_anomaly(preprocessed_data, consumption_kw)
            
            # Calculate efficiency score (compared to baseline)
            efficiency_score = self._calculate_efficiency(consumption_kw)
            
            # Confidence based on data quality
            confidence = 0.85 if len(self.consumption_history) > 1000 else 0.70
            
            return {
                "consumption_kwh": round(consumption_kwh, 2),
                "efficiency_score": round(efficiency_score, 2),
                "anomaly_score": round(anomaly_score, 3),
                "is_anomaly": is_anomaly,
                "baseline_consumption": round(self.baseline_consumption, 2),
                "confidence": round(confidence, 2)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            # Return safe defaults on error
            return {
                "consumption_kwh": 100.0,
                "efficiency_score": 50.0,
                "anomaly_score": 0.5,
                "is_anomaly": False,
                "baseline_consumption": self.baseline_consumption,
                "confidence": 0.0
            }
    
    def _detect_anomaly(self, preprocessed_data: np.ndarray, consumption: float) -> tuple:
        """
        Detect anomalies using Isolation Forest or heuristics.
        
        Returns:
            Tuple of (anomaly_score, is_anomaly)
        """
        if self.anomaly_model is not None:
            try:
                # Flatten sequence for Isolation Forest
                features = preprocessed_data[0].flatten()
                anomaly_score = self.anomaly_model.decision_function([features])[0]
                # Normalize to 0-1 (higher = more anomalous)
                anomaly_score = (anomaly_score - (-0.5)) / (0.5 - (-0.5))  # Rough normalization
                anomaly_score = max(0.0, min(1.0, anomaly_score))
                is_anomaly = anomaly_score > 0.6
                return anomaly_score, is_anomaly
            except Exception as e:
                logger.warning(f"Anomaly detection error: {e}")
        
        # Heuristic-based anomaly detection
        deviation = abs(consumption - self.baseline_consumption) / self.baseline_consumption
        anomaly_score = min(1.0, deviation * 2.0)  # Scale deviation to 0-1
        is_anomaly = deviation > 0.3  # 30% deviation threshold
        
        return anomaly_score, is_anomaly
    
    def _calculate_efficiency(self, consumption: float) -> float:
        """
        Calculate efficiency score (0-100) based on consumption vs baseline.
        
        Args:
            consumption: Current consumption in kW
            
        Returns:
            Efficiency score (0-100, higher = more efficient)
        """
        if self.baseline_consumption == 0:
            return 50.0
        
        # Efficiency = how much lower than baseline (up to 100%)
        ratio = consumption / self.baseline_consumption
        
        if ratio <= 0.8:  # 20% or more below baseline = excellent
            efficiency = 100.0
        elif ratio <= 1.0:  # At or below baseline = good
            efficiency = 80.0 + (1.0 - ratio) * 100.0  # 80-100
        elif ratio <= 1.2:  # Up to 20% above baseline = acceptable
            efficiency = 60.0 + (1.2 - ratio) * 100.0  # 60-80
        else:  # More than 20% above baseline = poor
            efficiency = max(0.0, 60.0 - (ratio - 1.2) * 100.0)  # 0-60
        
        return efficiency
    
    def _mock_predict(self, preprocessed_data: np.ndarray) -> Dict[str, Any]:
        """Mock prediction when model is not available."""
        # Extract average power from sequence
        avg_power = preprocessed_data[0, :, 0].mean()
        
        # Detect anomalies heuristically
        anomaly_score, is_anomaly = self._detect_anomaly(preprocessed_data, avg_power)
        
        # Calculate efficiency
        efficiency_score = self._calculate_efficiency(avg_power)
        
        return {
            "consumption_kwh": round(float(avg_power), 2),
            "efficiency_score": round(efficiency_score, 2),
            "anomaly_score": round(anomaly_score, 3),
            "is_anomaly": is_anomaly,
            "baseline_consumption": round(self.baseline_consumption, 2),
            "confidence": 0.70
        }
    
    def reset_buffer(self) -> None:
        """Reset the data buffer."""
        self.data_buffer.clear()
        logger.debug("Data buffer reset")

"""
PPE Agent Model Component
Handles CNN model for time-series classification of PPE compliance.
"""
import pickle
import numpy as np
from typing import Dict, Any, Optional, List
from collections import deque
import logging
from pathlib import Path

logger = logging.getLogger("PPEAgent.Model")


class PPEModel:
    """
    PPE Compliance Detection Model Component.
    
    Uses CNN for time-series classification of wearable sensor data.
    Implements smoothing buffer with majority vote.
    """
    
    def __init__(self, model_path: str, sequence_length: int = 10, num_features: int = 6, 
                 smoothing_buffer_size: int = 5, scaler_path: Optional[str] = None,
                 class_weights_path: Optional[str] = None):
        """
        Initialize model component.
        
        Args:
            model_path: Path to CNN model file (.keras or .pkl)
            sequence_length: Time window length for CNN
            num_features: Number of sensor features (6-axis IMU)
            smoothing_buffer_size: Size of smoothing buffer for majority vote
            scaler_path: Path to scaler pickle file (optional)
            class_weights_path: Path to class weights pickle file (optional)
        """
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.class_weights_path = class_weights_path
        self.sequence_length = sequence_length
        self.num_features = num_features
        self.smoothing_buffer_size = smoothing_buffer_size
        
        self.model = None
        self.scaler = None
        self.class_weights = None
        self.data_buffer: deque = deque(maxlen=sequence_length)
        
        # Smoothing buffer for majority vote
        self.prediction_buffer: deque = deque(maxlen=smoothing_buffer_size)
        
        logger.info(f"Initialized PPE Model (sequence_length={sequence_length}, "
                   f"num_features={num_features}, smoothing_buffer={smoothing_buffer_size})")
    
    def load_model(self) -> None:
        """Load CNN model from Keras or pickle file."""
        try:
            if not Path(self.model_path).exists():
                logger.warning(f"Model file not found: {self.model_path}. Using mock model.")
                self.model = None
            else:
                # Check if it's a Keras model
                if self.model_path.endswith('.keras') or self.model_path.endswith('.h5'):
                    try:
                        from tensorflow import keras
                        self.model = keras.models.load_model(self.model_path)
                        logger.info(f"Loaded Keras CNN model from {self.model_path}")
                    except ImportError:
                        logger.error("TensorFlow/Keras not available. Install with: pip install tensorflow")
                        self.model = None
                    except Exception as e:
                        logger.error(f"Failed to load Keras model: {e}", exc_info=True)
                        self.model = None
                else:
                    # Load pickle model
                    with open(self.model_path, 'rb') as f:
                        self.model = pickle.load(f)
                    logger.info(f"Loaded pickle model from {self.model_path}")
            
            # Load scaler if provided
            if self.scaler_path and Path(self.scaler_path).exists():
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info(f"Loaded scaler from {self.scaler_path}")
            
            # Load class weights if provided
            if self.class_weights_path and Path(self.class_weights_path).exists():
                with open(self.class_weights_path, 'rb') as f:
                    self.class_weights = pickle.load(f)
                logger.info(f"Loaded class weights from {self.class_weights_path}")
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            self.model = None
    
    def preprocess(self, raw_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Preprocess raw sensor data into model input format.
        
        Features: 6-axis IMU data (accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z)
        
        Args:
            raw_data: Dictionary with sensor readings
            
        Returns:
            Preprocessed array of shape (1, sequence_length, num_features) or None if insufficient data
        """
        try:
            # Extract sensor features
            sensors = self._extract_features(raw_data)
            
            # Add to buffer
            self.data_buffer.append(sensors)
            
            # Check if we have enough data
            if len(self.data_buffer) < self.sequence_length:
                logger.debug(f"Insufficient data: {len(self.data_buffer)}/{self.sequence_length}")
                return None
            
            # Convert buffer to array
            sequence = np.array(list(self.data_buffer))
            
            # Apply scaler if available
            if self.scaler is not None:
                sequence = self.scaler.transform(sequence)
            
            # Reshape for CNN: (1, sequence_length, num_features, 1) or (1, sequence_length, num_features)
            sequence = sequence.reshape(1, self.sequence_length, self.num_features)
            
            return sequence
            
        except Exception as e:
            logger.error(f"Preprocessing error: {e}", exc_info=True)
            return None
    
    def _extract_features(self, raw_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract 6-axis IMU features from raw data.
        
        Features:
        0-2: Accelerometer (x, y, z)
        3-5: Gyroscope (x, y, z)
        """
        # Try to get sensors array or individual values
        if 'sensors' in raw_data and isinstance(raw_data['sensors'], list):
            sensors = raw_data['sensors']
            if len(sensors) >= 6:
                return np.array(sensors[:6])
        
        # Fallback to individual fields
        accel_x = float(raw_data.get('accel_x', raw_data.get('ax', 0.0)))
        accel_y = float(raw_data.get('accel_y', raw_data.get('ay', 0.0)))
        accel_z = float(raw_data.get('accel_z', raw_data.get('az', 0.0)))
        gyro_x = float(raw_data.get('gyro_x', raw_data.get('gx', 0.0)))
        gyro_y = float(raw_data.get('gyro_y', raw_data.get('gy', 0.0)))
        gyro_z = float(raw_data.get('gyro_z', raw_data.get('gz', 0.0)))
        
        return np.array([accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z])
    
    def predict(self, preprocessed_data: np.ndarray) -> Dict[str, Any]:
        """
        Run model inference on preprocessed data with smoothing buffer.
        
        Args:
            preprocessed_data: Preprocessed array of shape (1, sequence_length, num_features)
            
        Returns:
            Dictionary with prediction results:
            - helmet_compliant: Boolean
            - vest_compliant: Boolean
            - gloves_compliant: Boolean
            - overall_compliance: Boolean
            - compliance_rate: Compliance rate (0-100)
            - confidence: Prediction confidence (0-1)
        """
        try:
            if self.model is None:
                return self._mock_predict(preprocessed_data)
            
            # Run CNN inference
            if hasattr(self.model, 'predict'):
                prediction = self.model.predict(preprocessed_data, verbose=0)
            else:
                # Fallback for non-Keras models
                prediction = self.model.predict(preprocessed_data)
            
            # Handle different model output formats
            if isinstance(prediction, (list, tuple)):
                prediction = prediction[0]
            
            if isinstance(prediction, np.ndarray):
                if prediction.ndim > 1:
                    prediction = prediction[0]
            
            # Interpret prediction (assuming model outputs probabilities or class indices)
            # Keras models typically output probabilities for each class
            if len(prediction) >= 3:
                # Model outputs probabilities for helmet, vest, gloves (or 3 classes)
                helmet_prob = float(prediction[0])
                vest_prob = float(prediction[1])
                gloves_prob = float(prediction[2])
            elif len(prediction) == 2:
                # Binary classification: [not_compliant_prob, compliant_prob]
                compliant_prob = float(prediction[1]) if len(prediction) > 1 else float(prediction[0])
                helmet_prob = vest_prob = gloves_prob = compliant_prob
            else:
                # Single output - interpret as overall compliance
                overall_prob = float(prediction[0]) if len(prediction) > 0 else 0.5
                helmet_prob = vest_prob = gloves_prob = overall_prob
            
            # Apply threshold
            threshold = 0.5
            helmet_compliant = helmet_prob > threshold
            vest_compliant = vest_prob > threshold
            gloves_compliant = gloves_prob > threshold
            
            # Add to smoothing buffer
            self.prediction_buffer.append({
                'helmet': helmet_compliant,
                'vest': vest_compliant,
                'gloves': gloves_compliant
            })
            
            # Apply majority vote smoothing
            helmet_compliant, vest_compliant, gloves_compliant = self._apply_smoothing()
            
            # Calculate overall compliance
            overall_compliance = helmet_compliant and vest_compliant and gloves_compliant
            compliance_rate = (int(helmet_compliant) + int(vest_compliant) + int(gloves_compliant)) / 3.0 * 100.0
            
            confidence = 0.85 if len(self.prediction_buffer) >= self.smoothing_buffer_size else 0.70
            
            return {
                "helmet_compliant": helmet_compliant,
                "vest_compliant": vest_compliant,
                "gloves_compliant": gloves_compliant,
                "overall_compliance": overall_compliance,
                "compliance_rate": round(compliance_rate, 2),
                "confidence": round(confidence, 2)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            return {
                "helmet_compliant": False,
                "vest_compliant": False,
                "gloves_compliant": False,
                "overall_compliance": False,
                "compliance_rate": 0.0,
                "confidence": 0.0
            }
    
    def _apply_smoothing(self) -> tuple:
        """
        Apply majority vote smoothing over prediction buffer.
        
        Returns:
            Tuple of (helmet_compliant, vest_compliant, gloves_compliant)
        """
        if len(self.prediction_buffer) == 0:
            return (False, False, False)
        
        # Count votes
        helmet_votes = sum(1 for p in self.prediction_buffer if p['helmet'])
        vest_votes = sum(1 for p in self.prediction_buffer if p['vest'])
        gloves_votes = sum(1 for p in self.prediction_buffer if p['gloves'])
        
        total = len(self.prediction_buffer)
        threshold = total / 2.0  # Majority threshold
        
        helmet_compliant = helmet_votes > threshold
        vest_compliant = vest_votes > threshold
        gloves_compliant = gloves_votes > threshold
        
        return (helmet_compliant, vest_compliant, gloves_compliant)
    
    def _mock_predict(self, preprocessed_data: np.ndarray) -> Dict[str, Any]:
        """Mock prediction when model is not available."""
        # Simple heuristic based on sensor variance
        sensor_variance = np.var(preprocessed_data[0], axis=0).mean()
        
        # Low variance = likely wearing (still), high variance = likely not wearing (moving)
        # This is a simplified heuristic
        compliance_prob = 1.0 - min(1.0, sensor_variance / 10.0)
        
        helmet_compliant = compliance_prob > 0.6
        vest_compliant = compliance_prob > 0.5
        gloves_compliant = compliance_prob > 0.7
        
        # Add to smoothing buffer
        self.prediction_buffer.append({
            'helmet': helmet_compliant,
            'vest': vest_compliant,
            'gloves': gloves_compliant
        })
        
        # Apply smoothing
        helmet_compliant, vest_compliant, gloves_compliant = self._apply_smoothing()
        
        overall_compliance = helmet_compliant and vest_compliant and gloves_compliant
        compliance_rate = (int(helmet_compliant) + int(vest_compliant) + int(gloves_compliant)) / 3.0 * 100.0
        
        return {
            "helmet_compliant": helmet_compliant,
            "vest_compliant": vest_compliant,
            "gloves_compliant": gloves_compliant,
            "overall_compliance": overall_compliance,
            "compliance_rate": round(compliance_rate, 2),
            "confidence": 0.70
        }
    
    def reset_buffer(self) -> None:
        """Reset the data buffer."""
        self.data_buffer.clear()
        self.prediction_buffer.clear()
        logger.debug("Data buffers reset")


"""
Hazard Agent Model Component
Handles Random Forest classifier for workplace hazard detection.
"""
import pickle
import numpy as np
from typing import Dict, Any, Optional
import logging
from pathlib import Path

logger = logging.getLogger("HazardAgent.Model")


class HazardModel:
    """
    Workplace Hazard Detection Model Component.
    
    Uses Random Forest classifier for hazard detection.
    Supports zone-based hazard tracking.
    """
    
    def __init__(self, model_path: str, num_features: int = 6, scaler_path: Optional[str] = None,
                 label_encoders_path: Optional[str] = None):
        """
        Initialize model component.
        
        Args:
            model_path: Path to Random Forest model pickle file
            num_features: Number of input features
            scaler_path: Path to standard scaler pickle file (optional)
            label_encoders_path: Path to label encoders pickle file (optional)
        """
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.label_encoders_path = label_encoders_path
        self.num_features = num_features
        self.model = None
        self.scaler = None
        self.label_encoders = None
        logger.info(f"Initialized Hazard Model (num_features={num_features})")
    
    def load_model(self) -> None:
        """Load Random Forest model, scaler, and label encoders from pickle files."""
        try:
            if not Path(self.model_path).exists():
                logger.warning(f"Model file not found: {self.model_path}. Using mock model.")
                self.model = None
            else:
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded Random Forest model from {self.model_path}")
            
            # Load scaler if provided
            if self.scaler_path and Path(self.scaler_path).exists():
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
                logger.info(f"Loaded scaler from {self.scaler_path}")
            
            # Load label encoders if provided
            if self.label_encoders_path and Path(self.label_encoders_path).exists():
                with open(self.label_encoders_path, 'rb') as f:
                    self.label_encoders = pickle.load(f)
                logger.info(f"Loaded label encoders from {self.label_encoders_path}")
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            self.model = None
            self.scaler = None
            self.label_encoders = None
    
    def preprocess(self, raw_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Preprocess raw sensor data.
        
        Features: temperature, vibration, pressure, gas_level, noise_level, zone_id
        
        Args:
            raw_data: Dictionary with sensor readings
            
        Returns:
            Preprocessed array of shape (1, num_features)
        """
        try:
            features = self._extract_features(raw_data)
            return features.reshape(1, -1)
        except Exception as e:
            logger.error(f"Preprocessing error: {e}", exc_info=True)
            return None
    
    def _extract_features(self, raw_data: Dict[str, Any]) -> np.ndarray:
        """Extract features from raw data."""
        temp = float(raw_data.get('temperature', raw_data.get('Temperature_C', 20.0)))
        vibration = float(raw_data.get('vibration', raw_data.get('Vibration_Hz', 0.5)))
        pressure = float(raw_data.get('pressure', raw_data.get('Pressure_psi', 100.0)))
        gas_level = float(raw_data.get('gas_level', raw_data.get('Gas_Level_ppm', 0.0)))
        noise_level = float(raw_data.get('noise_level', raw_data.get('Noise_dB', 60.0)))
        zone_id = float(raw_data.get('zone_id', raw_data.get('Zone_ID', 0.0)))
        
        return np.array([temp, vibration, pressure, gas_level, noise_level, zone_id])
    
    def predict(self, preprocessed_data: np.ndarray) -> Dict[str, Any]:
        """
        Run model inference.
        
        Returns:
            Dictionary with:
            - hazard_score: Hazard probability (0-1)
            - hazard_type: Type of hazard detected
            - safety_score: Safety score (0-100)
            - confidence: Prediction confidence
        """
        try:
            if self.model is None:
                return self._mock_predict(preprocessed_data)
            
            # Random Forest prediction
            hazard_prob = self.model.predict_proba(preprocessed_data)[0]
            hazard_class = self.model.predict(preprocessed_data)[0]
            
            # Get hazard score (probability of hazard class)
            hazard_score = float(hazard_prob[1] if len(hazard_prob) > 1 else hazard_prob[0])
            safety_score = (1.0 - hazard_score) * 100.0
            
            hazard_type = "UNKNOWN"
            if hazard_score > 0.7:
                # Determine hazard type from features
                if preprocessed_data[0, 0] > 80:  # High temperature
                    hazard_type = "FIRE_RISK"
                elif preprocessed_data[0, 3] > 50:  # High gas
                    hazard_type = "GAS_LEAK"
                elif preprocessed_data[0, 4] > 90:  # High noise
                    hazard_type = "NOISE_HAZARD"
                else:
                    hazard_type = "GENERAL_HAZARD"
            
            return {
                "hazard_score": round(hazard_score, 3),
                "hazard_type": hazard_type,
                "safety_score": round(safety_score, 2),
                "confidence": 0.85
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            return {
                "hazard_score": 0.0,
                "hazard_type": "NONE",
                "safety_score": 100.0,
                "confidence": 0.0
            }
    
    def _mock_predict(self, preprocessed_data: np.ndarray) -> Dict[str, Any]:
        """Mock prediction when model is not available."""
        temp = preprocessed_data[0, 0]
        gas = preprocessed_data[0, 3]
        
        # Heuristic: high temp or gas = hazard
        hazard_score = max(0.0, min(1.0, (temp - 70) / 30.0 + (gas - 20) / 80.0))
        safety_score = (1.0 - hazard_score) * 100.0
        
        hazard_type = "NONE"
        if hazard_score > 0.7:
            hazard_type = "FIRE_RISK" if temp > 80 else "GAS_LEAK"
        
        return {
            "hazard_score": round(hazard_score, 3),
            "hazard_type": hazard_type,
            "safety_score": round(safety_score, 2),
            "confidence": 0.70
        }

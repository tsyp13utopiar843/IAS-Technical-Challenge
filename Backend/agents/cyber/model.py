"""
Cyber Agent Model Component
Handles Isolation Forest model for anomaly detection in network traffic.
"""
import pickle
import numpy as np
from typing import Dict, Any, Optional
from collections import deque
import logging
from pathlib import Path

logger = logging.getLogger("CyberAgent.Model")


class CyberModel:
    """
    Cyber Threat Detection Model Component.
    
    Uses Isolation Forest for anomaly detection in network traffic.
    Tracks consecutive anomalies for escalation.
    """
    
    def __init__(self, model_path: str, sequence_length: int = 10, num_features: int = 4):
        """
        Initialize model component.
        
        Args:
            model_path: Path to Isolation Forest model pickle file
            sequence_length: Number of recent samples to track
            num_features: Number of input features
        """
        self.model_path = model_path
        self.sequence_length = sequence_length
        self.num_features = num_features
        
        self.model = None
        self.data_buffer: deque = deque(maxlen=sequence_length)
        
        # Consecutive anomaly counter
        self.consecutive_anomalies = 0
        
        logger.info(f"Initialized Cyber Model (sequence_length={sequence_length}, num_features={num_features})")
    
    def load_model(self) -> None:
        """Load Isolation Forest model from pickle file."""
        try:
            # Resolve path (handle relative paths from root)
            model_path = Path(self.model_path)
            if not model_path.is_absolute():
                # Try relative to current directory first, then from agent directory
                if not model_path.exists():
                    # Try from Backend root
                    root_path = Path(__file__).parent.parent.parent / self.model_path
                    if root_path.exists():
                        model_path = root_path
            
            if not model_path.exists():
                logger.warning(f"Model file not found: {model_path}. Using mock model.")
                self.model = None
            else:
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                logger.info(f"Loaded Isolation Forest model from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}", exc_info=True)
            self.model = None
    
    def preprocess(self, raw_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Preprocess raw network data into model input format.
        
        Features: latency, packet_loss, throughput, connection_count
        
        Args:
            raw_data: Dictionary with network readings
            
        Returns:
            Preprocessed array of shape (num_features,) or None if insufficient data
        """
        try:
            # Extract features
            features = self._extract_features(raw_data)
            
            # Add to buffer
            self.data_buffer.append(features)
            
            # Return single sample (Isolation Forest works on single samples)
            return features.reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Preprocessing error: {e}", exc_info=True)
            return None
    
    def _extract_features(self, raw_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract features from raw data.
        
        Features:
        0. latency (ms)
        1. packet_loss (%)
        2. throughput (Mbps, normalized)
        3. connection_count (normalized)
        """
        latency = float(raw_data.get('latency', raw_data.get('Network_Latency_ms', 5.0)))
        packet_loss = float(raw_data.get('packet_loss', raw_data.get('Packet_Loss_%', 0.0)))
        throughput = float(raw_data.get('throughput', raw_data.get('Throughput_Mbps', 100.0)))
        connection_count = float(raw_data.get('connection_count', raw_data.get('Connections', 10.0)))
        
        # Normalize features
        latency_norm = min(1.0, latency / 100.0)  # Normalize to 0-1 (100ms = 1.0)
        packet_loss_norm = min(1.0, packet_loss / 100.0)  # Already in %
        throughput_norm = min(1.0, throughput / 1000.0)  # Normalize to 0-1 (1Gbps = 1.0)
        connection_count_norm = min(1.0, connection_count / 1000.0)  # Normalize to 0-1
        
        return np.array([latency_norm, packet_loss_norm, throughput_norm, connection_count_norm])
    
    def predict(self, preprocessed_data: np.ndarray) -> Dict[str, Any]:
        """
        Run model inference on preprocessed data.
        
        Args:
            preprocessed_data: Preprocessed array of shape (1, num_features)
            
        Returns:
            Dictionary with prediction results:
            - anomaly_score: Anomaly score (0-1, higher = more anomalous)
            - is_anomaly: Boolean anomaly flag
            - threat_level: LOW, MEDIUM, HIGH, CRITICAL
            - consecutive_anomalies: Number of consecutive anomalies
            - confidence: Prediction confidence (0-1)
        """
        try:
            if self.model is None:
                return self._mock_predict(preprocessed_data)
            
            # Run Isolation Forest inference
            anomaly_score = self.model.decision_function(preprocessed_data)[0]
            is_anomaly = self.model.predict(preprocessed_data)[0] == -1
            
            # Normalize anomaly score to 0-1 (higher = more anomalous)
            # Isolation Forest returns negative values for anomalies
            if is_anomaly:
                anomaly_score_normalized = min(1.0, abs(anomaly_score) / 0.5)
            else:
                anomaly_score_normalized = max(0.0, (0.5 + anomaly_score) / 0.5)
            
            # Update consecutive anomaly counter
            if is_anomaly:
                self.consecutive_anomalies += 1
            else:
                self.consecutive_anomalies = 0
            
            # Determine threat level
            threat_level = self._determine_threat_level(anomaly_score_normalized, self.consecutive_anomalies)
            
            confidence = 0.85 if len(self.data_buffer) > 5 else 0.70
            
            return {
                "anomaly_score": round(anomaly_score_normalized, 3),
                "is_anomaly": bool(is_anomaly),
                "threat_level": threat_level,
                "consecutive_anomalies": self.consecutive_anomalies,
                "confidence": round(confidence, 2)
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            return {
                "anomaly_score": 0.5,
                "is_anomaly": False,
                "threat_level": "LOW",
                "consecutive_anomalies": 0,
                "confidence": 0.0
            }
    
    def _determine_threat_level(self, anomaly_score: float, consecutive: int) -> str:
        """Determine threat level based on anomaly score and consecutive count."""
        if consecutive >= 5 or anomaly_score > 0.9:
            return "CRITICAL"
        elif consecutive >= 3 or anomaly_score > 0.7:
            return "HIGH"
        elif consecutive >= 1 or anomaly_score > 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _mock_predict(self, preprocessed_data: np.ndarray) -> Dict[str, Any]:
        """Mock prediction when model is not available."""
        latency_norm = preprocessed_data[0, 0]
        
        # Heuristic: high latency = anomaly
        is_anomaly = latency_norm > 0.5
        anomaly_score = latency_norm
        
        if is_anomaly:
            self.consecutive_anomalies += 1
        else:
            self.consecutive_anomalies = 0
        
        threat_level = self._determine_threat_level(anomaly_score, self.consecutive_anomalies)
        
        return {
            "anomaly_score": round(anomaly_score, 3),
            "is_anomaly": is_anomaly,
            "threat_level": threat_level,
            "consecutive_anomalies": self.consecutive_anomalies,
            "confidence": 0.70
        }
    
    def reset_consecutive(self) -> None:
        """Reset consecutive anomaly counter."""
        self.consecutive_anomalies = 0
        logger.debug("Consecutive anomaly counter reset")

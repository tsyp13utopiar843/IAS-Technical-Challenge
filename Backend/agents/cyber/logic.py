"""
Cyber Agent Logic Component
Decision rules engine for cyber threat detection alerts and actions.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger("CyberAgent.Logic")


class CyberLogic:
    """Cyber Threat Detection Logic Component."""
    
    def __init__(self, thresholds: Dict[str, Any]):
        """Initialize logic component."""
        self.consecutive_threshold = thresholds.get('consecutive_threshold', 5)
        self.critical_anomaly_score = thresholds.get('critical_anomaly_score', 0.9)
        self.high_anomaly_score = thresholds.get('high_anomaly_score', 0.7)
        
        logger.info(f"Initialized Cyber Logic (consecutive_threshold={self.consecutive_threshold})")
    
    def apply_logic(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules to model prediction."""
        try:
            anomaly_score = prediction.get('anomaly_score', 0.0)
            is_anomaly = prediction.get('is_anomaly', False)
            threat_level = prediction.get('threat_level', 'LOW')
            consecutive = prediction.get('consecutive_anomalies', 0)
            
            alert_level, action, priority, recommended_action = self._determine_alert(
                threat_level, anomaly_score, consecutive, is_anomaly
            )
            
            return {
                "alert_level": alert_level,
                "action": action,
                "priority": priority,
                "recommended_action": recommended_action,
                "threat_level": threat_level,
                "anomaly_score": anomaly_score,
                "consecutive_anomalies": consecutive,
                "is_anomaly": is_anomaly
            }
            
        except Exception as e:
            logger.error(f"Logic processing error: {e}", exc_info=True)
            return {
                "alert_level": "WARNING",
                "action": "INVESTIGATE",
                "priority": 3,
                "recommended_action": "Error in logic processing",
                "threat_level": "LOW",
                "anomaly_score": 0.0,
                "consecutive_anomalies": 0,
                "is_anomaly": False
            }
    
    def _determine_alert(self, threat_level: str, anomaly_score: float, 
                        consecutive: int, is_anomaly: bool) -> tuple:
        """Determine alert level and action."""
        if threat_level == "CRITICAL" or consecutive >= self.consecutive_threshold:
            return (
                "CRITICAL",
                "IMMEDIATE_RESPONSE",
                1,
                f"Critical cyber threat detected. Threat level: {threat_level}, "
                f"Anomaly score: {anomaly_score:.2f}, Consecutive anomalies: {consecutive}. "
                f"Activate incident response protocol immediately."
            )
        
        if threat_level == "HIGH":
            return (
                "WARNING",
                "INVESTIGATE",
                2,
                f"High threat level detected. Threat level: {threat_level}, "
                f"Anomaly score: {anomaly_score:.2f}. Investigate network activity."
            )
        
        if threat_level == "MEDIUM" or is_anomaly:
            return (
                "CAUTION",
                "MONITOR",
                3,
                f"Anomaly detected. Threat level: {threat_level}, "
                f"Anomaly score: {anomaly_score:.2f}. Continue monitoring."
            )
        
        return (
            "NORMAL",
            "MONITOR",
            4,
            f"Network status normal. Threat level: {threat_level}."
        )


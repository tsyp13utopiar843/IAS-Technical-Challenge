"""
PM Agent Logic Component
Decision rules engine for predictive maintenance alerts and actions.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger("PMAgent.Logic")


class PMLogic:
    """
    Predictive Maintenance Logic Component.
    
    Applies business rules to model predictions to determine:
    - Alert levels (NORMAL, CAUTION, WARNING, CRITICAL, EMERGENCY)
    - Recommended actions
    - Priority levels
    """
    
    def __init__(self, thresholds: Dict[str, float]):
        """
        Initialize logic component.
        
        Args:
            thresholds: Dictionary with threshold values:
                - critical_rul: RUL threshold for CRITICAL (hours)
                - warning_rul: RUL threshold for WARNING (hours)
                - caution_rul: RUL threshold for CAUTION (hours)
                - critical_failure_prob: Failure probability threshold for EMERGENCY
        """
        self.critical_rul = thresholds.get('critical_rul', 24.0)
        self.warning_rul = thresholds.get('warning_rul', 72.0)
        self.caution_rul = thresholds.get('caution_rul', 168.0)
        self.critical_failure_prob = thresholds.get('critical_failure_prob', 0.8)
        
        logger.info(f"Initialized PM Logic (thresholds: critical={self.critical_rul}h, "
                   f"warning={self.warning_rul}h, caution={self.caution_rul}h)")
    
    def apply_logic(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply business rules to model prediction.
        
        Args:
            prediction: Model prediction output with:
                - rul_hours: Remaining Useful Life in hours
                - health_score: Health score (0-100)
                - failure_probability: Probability of failure (0-1)
                - confidence: Prediction confidence (0-1)
        
        Returns:
            Dictionary with:
                - alert_level: NORMAL, CAUTION, WARNING, CRITICAL, EMERGENCY
                - action: Recommended action string
                - priority: 1-5 (1=highest)
                - recommended_action: Detailed action description
        """
        try:
            rul_hours = prediction.get('rul_hours', 0.0)
            failure_prob = prediction.get('failure_probability', 0.0)
            health_score = prediction.get('health_score', 0.0)
            
            # Determine alert level based on RUL and failure probability
            alert_level, action, priority, recommended_action = self._determine_alert(
                rul_hours, failure_prob, health_score
            )
            
            return {
                "alert_level": alert_level,
                "action": action,
                "priority": priority,
                "recommended_action": recommended_action,
                "rul_hours": rul_hours,
                "health_score": health_score,
                "failure_probability": failure_prob
            }
            
        except Exception as e:
            logger.error(f"Logic processing error: {e}", exc_info=True)
            return {
                "alert_level": "WARNING",
                "action": "INVESTIGATE",
                "priority": 3,
                "recommended_action": "Error in logic processing - manual investigation required",
                "rul_hours": prediction.get('rul_hours', 0.0),
                "health_score": prediction.get('health_score', 0.0),
                "failure_probability": prediction.get('failure_probability', 0.0)
            }
    
    def _determine_alert(self, rul_hours: float, failure_prob: float, health_score: float) -> tuple:
        """
        Determine alert level and action based on thresholds.
        
        Returns:
            Tuple of (alert_level, action, priority, recommended_action)
        """
        # Emergency shutdown: Very high failure probability
        if failure_prob >= self.critical_failure_prob:
            return (
                "EMERGENCY",
                "EMERGENCY_SHUTDOWN",
                1,
                f"Immediate shutdown required. Failure probability: {failure_prob:.1%}. "
                f"RUL: {rul_hours:.1f} hours. Contact maintenance team immediately."
            )
        
        # Critical: RUL < 24 hours
        if rul_hours < self.critical_rul:
            return (
                "CRITICAL",
                "IMMEDIATE_MAINTENANCE",
                1,
                f"Critical condition detected. RUL: {rul_hours:.1f} hours. "
                f"Schedule immediate maintenance within 24 hours. "
                f"Health score: {health_score:.1f}%."
            )
        
        # Warning: RUL < 72 hours
        if rul_hours < self.warning_rul:
            return (
                "WARNING",
                "SCHEDULE_72H",
                2,
                f"Warning condition. RUL: {rul_hours:.1f} hours. "
                f"Schedule maintenance within 72 hours. "
                f"Health score: {health_score:.1f}%."
            )
        
        # Caution: RUL < 168 hours (1 week)
        if rul_hours < self.caution_rul:
            return (
                "CAUTION",
                "PLAN_1WEEK",
                3,
                f"Caution condition. RUL: {rul_hours:.1f} hours. "
                f"Plan maintenance within 1 week. "
                f"Health score: {health_score:.1f}%."
            )
        
        # Normal: RUL >= 168 hours
        return (
            "NORMAL",
            "MONITOR",
            4,
            f"Normal condition. RUL: {rul_hours:.1f} hours. "
            f"Continue monitoring. Health score: {health_score:.1f}%."
        )


"""
Hazard Agent Logic Component
Decision rules engine for workplace hazard detection alerts and actions.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger("HazardAgent.Logic")


class HazardLogic:
    """Workplace Hazard Detection Logic Component."""
    
    def __init__(self, thresholds: Dict[str, Any]):
        """Initialize logic component."""
        self.critical_hazard_score = thresholds.get('critical_hazard_score', 0.8)
        self.warning_hazard_score = thresholds.get('warning_hazard_score', 0.5)
        self.evacuation_threshold = thresholds.get('evacuation_threshold', 0.9)
        self.safety_score_threshold = thresholds.get('safety_score_threshold', 40.0)
        
        logger.info(f"Initialized Hazard Logic (critical={self.critical_hazard_score}, "
                   f"evacuation={self.evacuation_threshold})")
    
    def apply_logic(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules to model prediction."""
        try:
            hazard_score = prediction.get('hazard_score', 0.0)
            hazard_type = prediction.get('hazard_type', 'NONE')
            safety_score = prediction.get('safety_score', 100.0)
            
            alert_level, action, priority, recommended_action, evacuation_required = self._determine_alert(
                hazard_score, hazard_type, safety_score
            )
            
            return {
                "alert_level": alert_level,
                "action": action,
                "priority": priority,
                "recommended_action": recommended_action,
                "evacuation_required": evacuation_required,
                "hazard_score": hazard_score,
                "hazard_type": hazard_type,
                "safety_score": safety_score
            }
            
        except Exception as e:
            logger.error(f"Logic processing error: {e}", exc_info=True)
            return {
                "alert_level": "WARNING",
                "action": "INVESTIGATE",
                "priority": 3,
                "recommended_action": "Error in logic processing - manual investigation required",
                "evacuation_required": False,
                "hazard_score": prediction.get('hazard_score', 0.0),
                "hazard_type": prediction.get('hazard_type', 'NONE'),
                "safety_score": prediction.get('safety_score', 100.0)
            }
    
    def _determine_alert(self, hazard_score: float, hazard_type: str, safety_score: float) -> tuple:
        """Determine alert level and action based on thresholds."""
        # Emergency evacuation
        if hazard_score >= self.evacuation_threshold:
            return (
                "EMERGENCY",
                "EVACUATE",
                1,
                f"EMERGENCY EVACUATION REQUIRED! Hazard score: {hazard_score:.2f}, "
                f"Type: {hazard_type}, Safety score: {safety_score:.1f}%. "
                f"Initiate evacuation protocol immediately.",
                True
            )
        
        # Critical hazard
        if hazard_score >= self.critical_hazard_score or safety_score < self.safety_score_threshold:
            return (
                "CRITICAL",
                "IMMEDIATE_RESPONSE",
                1,
                f"Critical workplace hazard detected. Hazard score: {hazard_score:.2f}, "
                f"Type: {hazard_type}, Safety score: {safety_score:.1f}%. "
                f"Activate emergency response protocol.",
                False
            )
        
        # Warning
        if hazard_score >= self.warning_hazard_score:
            return (
                "WARNING",
                "INVESTIGATE",
                2,
                f"Workplace hazard detected. Hazard score: {hazard_score:.2f}, "
                f"Type: {hazard_type}, Safety score: {safety_score:.1f}%. "
                f"Investigate and take preventive measures.",
                False
            )
        
        # Caution
        if hazard_score > 0.2:
            return (
                "CAUTION",
                "MONITOR",
                3,
                f"Elevated hazard risk. Hazard score: {hazard_score:.2f}, "
                f"Safety score: {safety_score:.1f}%. Continue monitoring.",
                False
            )
        
        # Normal
        return (
            "NORMAL",
            "MONITOR",
            4,
            f"Workplace safety status normal. Safety score: {safety_score:.1f}%.",
            False
        )


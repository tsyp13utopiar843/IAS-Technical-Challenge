"""
PPE Agent Logic Component
Decision rules engine for PPE compliance alerts and actions.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger("PPEAgent.Logic")


class PPELogic:
    """PPE Compliance Detection Logic Component."""
    
    def __init__(self, thresholds: Dict[str, Any]):
        """Initialize logic component."""
        self.critical_compliance_rate = thresholds.get('critical_compliance_rate', 50.0)
        self.warning_compliance_rate = thresholds.get('warning_compliance_rate', 75.0)
        self.required_items = thresholds.get('required_items', ['helmet', 'vest', 'gloves'])
        
        logger.info(f"Initialized PPE Logic (critical_rate={self.critical_compliance_rate}, "
                   f"warning_rate={self.warning_compliance_rate})")
    
    def apply_logic(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules to model prediction."""
        try:
            compliance_rate = prediction.get('compliance_rate', 0.0)
            overall_compliance = prediction.get('overall_compliance', False)
            helmet_compliant = prediction.get('helmet_compliant', False)
            vest_compliant = prediction.get('vest_compliant', False)
            gloves_compliant = prediction.get('gloves_compliant', False)
            
            # Count violations
            violations = []
            if 'helmet' in self.required_items and not helmet_compliant:
                violations.append('helmet')
            if 'vest' in self.required_items and not vest_compliant:
                violations.append('vest')
            if 'gloves' in self.required_items and not gloves_compliant:
                violations.append('gloves')
            
            violations_count = len(violations)
            
            alert_level, action, priority, recommended_action, access_denied = self._determine_alert(
                compliance_rate, overall_compliance, violations_count, violations
            )
            
            return {
                "alert_level": alert_level,
                "action": action,
                "priority": priority,
                "recommended_action": recommended_action,
                "access_denied": access_denied,
                "violations": violations,
                "violations_count": violations_count,
                "compliance_rate": compliance_rate,
                "overall_compliance": overall_compliance
            }
            
        except Exception as e:
            logger.error(f"Logic processing error: {e}", exc_info=True)
            return {
                "alert_level": "WARNING",
                "action": "INVESTIGATE",
                "priority": 3,
                "recommended_action": "Error in logic processing - manual investigation required",
                "access_denied": False,
                "violations": [],
                "violations_count": 0,
                "compliance_rate": prediction.get('compliance_rate', 0.0),
                "overall_compliance": False
            }
    
    def _determine_alert(self, compliance_rate: float, overall_compliance: bool,
                        violations_count: int, violations: list) -> tuple:
        """Determine alert level and action based on thresholds."""
        # Critical: Multiple violations or very low compliance
        if violations_count >= 2 or compliance_rate < self.critical_compliance_rate:
            return (
                "CRITICAL",
                "DENY_ACCESS",
                1,
                f"Critical PPE violation detected. Compliance rate: {compliance_rate:.1f}%, "
                f"Violations: {', '.join(violations)}. Access denied. Immediate corrective action required.",
                True
            )
        
        # Warning: Single violation or low compliance
        if violations_count >= 1 or compliance_rate < self.warning_compliance_rate:
            return (
                "WARNING",
                "WARN_WORKER",
                2,
                f"PPE violation detected. Compliance rate: {compliance_rate:.1f}%, "
                f"Violations: {', '.join(violations)}. Worker notified. Corrective action required.",
                False
            )
        
        # Caution: Near threshold
        if compliance_rate < 90.0:
            return (
                "CAUTION",
                "MONITOR",
                3,
                f"PPE compliance below optimal. Compliance rate: {compliance_rate:.1f}%. Continue monitoring.",
                False
            )
        
        # Normal: Full compliance
        return (
            "NORMAL",
            "ALLOW_ACCESS",
            4,
            f"PPE compliance verified. Compliance rate: {compliance_rate:.1f}%. Access granted.",
            False
        )


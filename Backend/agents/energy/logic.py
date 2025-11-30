"""
Energy Agent Logic Component
Decision rules engine for energy optimization alerts and actions.
"""
from typing import Dict, Any
import logging

logger = logging.getLogger("EnergyAgent.Logic")


class EnergyLogic:
    """
    Energy Consumption Optimization Logic Component.
    
    Applies business rules to model predictions to determine:
    - Alert levels based on efficiency and anomalies
    - Optimization recommendations
    - Priority levels
    """
    
    def __init__(self, thresholds: Dict[str, float]):
        """
        Initialize logic component.
        
        Args:
            thresholds: Dictionary with threshold values:
                - critical_efficiency: Efficiency threshold for CRITICAL (0-100)
                - warning_efficiency: Efficiency threshold for WARNING (0-100)
                - anomaly_threshold: Anomaly score threshold for alerts
        """
        self.critical_efficiency = thresholds.get('critical_efficiency', 40.0)
        self.warning_efficiency = thresholds.get('warning_efficiency', 60.0)
        self.anomaly_threshold = thresholds.get('anomaly_threshold', 0.7)
        
        logger.info(f"Initialized Energy Logic (thresholds: critical_eff={self.critical_efficiency}, "
                   f"warning_eff={self.warning_efficiency}, anomaly={self.anomaly_threshold})")
    
    def apply_logic(self, prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply business rules to model prediction.
        
        Args:
            prediction: Model prediction output with:
                - consumption_kwh: Predicted consumption
                - efficiency_score: Efficiency score (0-100)
                - anomaly_score: Anomaly score (0-1)
                - is_anomaly: Boolean anomaly flag
                - baseline_consumption: Baseline consumption
        
        Returns:
            Dictionary with:
                - alert_level: NORMAL, CAUTION, WARNING, CRITICAL
                - action: Recommended action string
                - priority: 1-5 (1=highest)
                - recommended_action: Detailed action description
                - optimization_recommendations: List of optimization suggestions
        """
        try:
            efficiency = prediction.get('efficiency_score', 50.0)
            anomaly_score = prediction.get('anomaly_score', 0.0)
            is_anomaly = prediction.get('is_anomaly', False)
            consumption = prediction.get('consumption_kwh', 100.0)
            baseline = prediction.get('baseline_consumption', 100.0)
            
            # Determine alert level
            alert_level, action, priority, recommended_action, optimizations = self._determine_alert(
                efficiency, anomaly_score, is_anomaly, consumption, baseline
            )
            
            return {
                "alert_level": alert_level,
                "action": action,
                "priority": priority,
                "recommended_action": recommended_action,
                "optimization_recommendations": optimizations,
                "consumption_kwh": consumption,
                "efficiency_score": efficiency,
                "anomaly_score": anomaly_score,
                "is_anomaly": is_anomaly
            }
            
        except Exception as e:
            logger.error(f"Logic processing error: {e}", exc_info=True)
            return {
                "alert_level": "WARNING",
                "action": "INVESTIGATE",
                "priority": 3,
                "recommended_action": "Error in logic processing - manual investigation required",
                "optimization_recommendations": [],
                "consumption_kwh": prediction.get('consumption_kwh', 0.0),
                "efficiency_score": prediction.get('efficiency_score', 0.0),
                "anomaly_score": prediction.get('anomaly_score', 0.0),
                "is_anomaly": False
            }
    
    def _determine_alert(self, efficiency: float, anomaly_score: float, is_anomaly: bool,
                        consumption: float, baseline: float) -> tuple:
        """
        Determine alert level and action based on thresholds.
        
        Returns:
            Tuple of (alert_level, action, priority, recommended_action, optimizations)
        """
        optimizations = []
        
        # Critical: Very low efficiency or high anomaly
        if efficiency < self.critical_efficiency or (is_anomaly and anomaly_score > 0.8):
            deviation = ((consumption - baseline) / baseline * 100) if baseline > 0 else 0
            
            optimizations = [
                "Immediate load reduction required",
                "Check for equipment malfunctions",
                "Review production schedule",
                "Consider peak shaving strategies"
            ]
            
            return (
                "CRITICAL",
                "IMMEDIATE_OPTIMIZATION",
                1,
                f"Critical energy inefficiency detected. Efficiency: {efficiency:.1f}%, "
                f"Consumption: {consumption:.1f} kWh (baseline: {baseline:.1f} kWh, "
                f"deviation: {deviation:+.1f}%). Anomaly detected: {is_anomaly}.",
                optimizations
            )
        
        # Warning: Low efficiency or moderate anomaly
        if efficiency < self.warning_efficiency or (is_anomaly and anomaly_score > self.anomaly_threshold):
            deviation = ((consumption - baseline) / baseline * 100) if baseline > 0 else 0
            
            optimizations = [
                "Review energy consumption patterns",
                "Optimize production scheduling",
                "Check equipment efficiency",
                "Consider load balancing"
            ]
            
            return (
                "WARNING",
                "OPTIMIZE_CONSUMPTION",
                2,
                f"Energy efficiency below optimal. Efficiency: {efficiency:.1f}%, "
                f"Consumption: {consumption:.1f} kWh (baseline: {baseline:.1f} kWh). "
                f"Anomaly detected: {is_anomaly}.",
                optimizations
            )
        
        # Caution: Slightly below optimal
        if efficiency < 80.0:
            optimizations = [
                "Monitor consumption trends",
                "Review operational schedules"
            ]
            
            return (
                "CAUTION",
                "MONITOR",
                3,
                f"Energy efficiency slightly below optimal. Efficiency: {efficiency:.1f}%. "
                f"Continue monitoring.",
                optimizations
            )
        
        # Normal: Good efficiency
        return (
            "NORMAL",
            "MAINTAIN",
            4,
            f"Energy consumption is optimal. Efficiency: {efficiency:.1f}%, "
            f"Consumption: {consumption:.1f} kWh.",
            []
        )


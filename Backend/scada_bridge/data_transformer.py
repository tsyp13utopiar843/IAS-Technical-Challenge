"""
Data Transformer Module
Converts JSON predictions from MQTT agents to protocol-specific formats.
"""
import logging
from typing import Dict, Any, Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transforms JSON predictions to OPC UA, Modbus, and DNP3 formats."""
    
    # String enum mappings
    ALERT_LEVEL_MAP = {
        "normal": 0,
        "warning": 1,
        "critical": 2,
        "unknown": 0
    }
    
    THREAT_LEVEL_MAP = {
        "low": 0,
        "medium": 1,
        "high": 2,
        "critical": 3,
        "unknown": 0
    }
    
    RISK_LEVEL_MAP = {
        "low": 0,
        "medium": 1,
        "high": 2,
        "unknown": 0
    }
    
    @staticmethod
    def safe_get(data: Dict, key: str, default: Any, data_type: type = str) -> Any:
        """Safely extract value from dict with type conversion and default fallback."""
        try:
            value = data.get(key, default)
            if value is None:
                return default
            return data_type(value)
        except (ValueError, TypeError) as e:
            logger.warning(f"Type conversion error for key '{key}': {e}. Using default: {default}")
            return default
    
    @staticmethod
    def parse_mqtt_prediction(payload: str) -> Optional[Dict[str, Any]]:
        """Parse MQTT JSON payload."""
        import json
        try:
            data = json.loads(payload)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
    
    @staticmethod
    def to_opcua(agent_id: str, prediction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform prediction data to OPC UA node values.
        Returns dict with node names as keys and values to write.
        """
        prediction = prediction_data.get("prediction", {})
        opcua_values = {}
        
        if agent_id == "pm_agent":
            opcua_values["RemainingUsefulLife"] = DataTransformer.safe_get(
                prediction, "rul_hours", 0.0, float
            )
            opcua_values["HealthScore"] = DataTransformer.safe_get(
                prediction, "health_score", 0.0, float
            )
            opcua_values["AlertLevel"] = DataTransformer.safe_get(
                prediction, "alert_level", "normal", str
            )
            opcua_values["FailureProbability"] = DataTransformer.safe_get(
                prediction, "failure_probability", 0.0, float
            )
            opcua_values["RecommendedAction"] = DataTransformer.safe_get(
                prediction, "recommended_action", "No action required", str
            )
        
        elif agent_id == "energy_agent":
            opcua_values["ConsumptionKWh"] = DataTransformer.safe_get(
                prediction, "consumption_kwh", 0.0, float
            )
            opcua_values["EfficiencyScore"] = DataTransformer.safe_get(
                prediction, "efficiency_score", 0.0, float
            )
            opcua_values["PredictedConsumption"] = DataTransformer.safe_get(
                prediction, "predicted_consumption", 0.0, float
            )
            opcua_values["IsAnomaly"] = DataTransformer.safe_get(
                prediction, "is_anomaly", False, bool
            )
            opcua_values["AnomalyScore"] = DataTransformer.safe_get(
                prediction, "anomaly_score", 0.0, float
            )
        
        elif agent_id == "cyber_agent":
            opcua_values["ThreatLevel"] = DataTransformer.safe_get(
                prediction, "threat_level", "low", str
            )
            opcua_values["AnomalyScore"] = DataTransformer.safe_get(
                prediction, "anomaly_score", 0.0, float
            )
            opcua_values["ActiveThreats"] = DataTransformer.safe_get(
                prediction, "active_threats", 0, int
            )
            opcua_values["NetworkHealth"] = DataTransformer.safe_get(
                prediction, "network_health", 100.0, float
            )
        
        elif agent_id == "hazard_agent":
            opcua_values["RiskLevel"] = DataTransformer.safe_get(
                prediction, "risk_level", "low", str
            )
            opcua_values["HazardCount"] = DataTransformer.safe_get(
                prediction, "hazard_count", 0, int
            )
            opcua_values["SafetyScore"] = DataTransformer.safe_get(
                prediction, "safety_score", 100.0, float
            )
            opcua_values["ActiveWarnings"] = DataTransformer.safe_get(
                prediction, "active_warnings", 0, int
            )
        
        elif agent_id == "ppe_agent":
            opcua_values["ComplianceRate"] = DataTransformer.safe_get(
                prediction, "compliance_rate", 100.0, float
            )
            opcua_values["ViolationsCount"] = DataTransformer.safe_get(
                prediction, "violations_count", 0, int
            )
            opcua_values["WorkersMonitored"] = DataTransformer.safe_get(
                prediction, "workers_monitored", 0, int
            )
            opcua_values["HelmetCompliance"] = DataTransformer.safe_get(
                prediction, "helmet_compliance", 100.0, float
            )
            opcua_values["VestCompliance"] = DataTransformer.safe_get(
                prediction, "vest_compliance", 100.0, float
            )
        
        return opcua_values
    
    @staticmethod
    def to_modbus(agent_id: str, prediction_data: Dict[str, Any]) -> Dict[int, int]:
        """
        Transform prediction data to Modbus register values (Int16).
        Returns dict with register addresses as keys and Int16 values.
        """
        prediction = prediction_data.get("prediction", {})
        modbus_values = {}
        
        if agent_id == "pm_agent":
            # Registers 0-99
            modbus_values[0] = int(DataTransformer.safe_get(prediction, "rul_hours", 0.0, float))
            modbus_values[1] = int(DataTransformer.safe_get(prediction, "health_score", 0.0, float))
            alert_level = DataTransformer.safe_get(prediction, "alert_level", "normal", str).lower()
            modbus_values[2] = DataTransformer.ALERT_LEVEL_MAP.get(alert_level, 0)
            modbus_values[3] = int(DataTransformer.safe_get(prediction, "failure_probability", 0.0, float) * 100)
        
        elif agent_id == "energy_agent":
            # Registers 100-199
            modbus_values[100] = int(DataTransformer.safe_get(prediction, "consumption_kwh", 0.0, float) * 10)
            modbus_values[101] = int(DataTransformer.safe_get(prediction, "efficiency_score", 0.0, float))
            modbus_values[102] = int(DataTransformer.safe_get(prediction, "predicted_consumption", 0.0, float) * 10)
            modbus_values[103] = 1 if DataTransformer.safe_get(prediction, "is_anomaly", False, bool) else 0
            modbus_values[104] = int(DataTransformer.safe_get(prediction, "anomaly_score", 0.0, float))
        
        elif agent_id == "cyber_agent":
            # Registers 200-299
            threat_level = DataTransformer.safe_get(prediction, "threat_level", "low", str).lower()
            modbus_values[200] = DataTransformer.THREAT_LEVEL_MAP.get(threat_level, 0)
            modbus_values[201] = int(DataTransformer.safe_get(prediction, "anomaly_score", 0.0, float))
            modbus_values[202] = DataTransformer.safe_get(prediction, "active_threats", 0, int)
            modbus_values[203] = int(DataTransformer.safe_get(prediction, "network_health", 100.0, float))
        
        elif agent_id == "hazard_agent":
            # Registers 300-399
            risk_level = DataTransformer.safe_get(prediction, "risk_level", "low", str).lower()
            modbus_values[300] = DataTransformer.RISK_LEVEL_MAP.get(risk_level, 0)
            modbus_values[301] = DataTransformer.safe_get(prediction, "hazard_count", 0, int)
            modbus_values[302] = int(DataTransformer.safe_get(prediction, "safety_score", 100.0, float))
            modbus_values[303] = DataTransformer.safe_get(prediction, "active_warnings", 0, int)
        
        elif agent_id == "ppe_agent":
            # Registers 400-499
            modbus_values[400] = int(DataTransformer.safe_get(prediction, "compliance_rate", 100.0, float))
            modbus_values[401] = DataTransformer.safe_get(prediction, "violations_count", 0, int)
            modbus_values[402] = DataTransformer.safe_get(prediction, "workers_monitored", 0, int)
            modbus_values[403] = int(DataTransformer.safe_get(prediction, "helmet_compliance", 100.0, float))
            modbus_values[404] = int(DataTransformer.safe_get(prediction, "vest_compliance", 100.0, float))
        
        return modbus_values
    
    @staticmethod
    def to_dnp3(agent_id: str, prediction_data: Dict[str, Any]) -> Dict[str, Dict[int, Union[float, bool]]]:
        """
        Transform prediction data to DNP3 point values.
        Returns dict with 'analog' and 'binary' keys containing point mappings.
        """
        prediction = prediction_data.get("prediction", {})
        dnp3_values = {"analog": {}, "binary": {}}
        
        if agent_id == "pm_agent":
            dnp3_values["analog"][0] = DataTransformer.safe_get(prediction, "rul_hours", 0.0, float)
            dnp3_values["analog"][1] = DataTransformer.safe_get(prediction, "health_score", 0.0, float)
            alert_level = DataTransformer.safe_get(prediction, "alert_level", "normal", str).lower()
            dnp3_values["binary"][0] = (alert_level == "critical")
        
        elif agent_id == "energy_agent":
            dnp3_values["analog"][2] = DataTransformer.safe_get(prediction, "consumption_kwh", 0.0, float)
            dnp3_values["analog"][3] = DataTransformer.safe_get(prediction, "efficiency_score", 0.0, float)
        
        elif agent_id == "cyber_agent":
            dnp3_values["analog"][4] = DataTransformer.safe_get(prediction, "anomaly_score", 0.0, float)
            active_threats = DataTransformer.safe_get(prediction, "active_threats", 0, int)
            dnp3_values["binary"][1] = (active_threats > 0)
        
        elif agent_id == "hazard_agent":
            dnp3_values["analog"][5] = DataTransformer.safe_get(prediction, "safety_score", 100.0, float)
            hazard_count = DataTransformer.safe_get(prediction, "hazard_count", 0, int)
            dnp3_values["binary"][2] = (hazard_count > 0)
        
        elif agent_id == "ppe_agent":
            dnp3_values["analog"][6] = DataTransformer.safe_get(prediction, "compliance_rate", 100.0, float)
            violations = DataTransformer.safe_get(prediction, "violations_count", 0, int)
            dnp3_values["binary"][3] = (violations > 0)
        
        return dnp3_values

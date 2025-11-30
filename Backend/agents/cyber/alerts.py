"""
Cyber Agent Alerts Component
Handles alert routing to multiple channels based on severity.
"""
import logging
from typing import Dict, Any, Optional

from agents.utils.alert_router import AlertRouter, AlertSeverity

logger = logging.getLogger("CyberAgent.Alerts")


class CyberAlerts:
    """Cyber Threat Detection Alerts Component."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any], mqtt_client: Optional[Any] = None):
        """Initialize alerts component."""
        self.agent_id = agent_id
        self.config = config
        self.mqtt_client = mqtt_client
        self.router = AlertRouter(config)
        logger.info(f"Initialized Cyber Alerts (channels: {len(config.get('channels', []))})")
    
    async def handle_alerts(self, logic_output: Dict[str, Any]) -> None:
        """Trigger alerts and actions based on logic output."""
        try:
            alert_level = logic_output.get('alert_level', 'NORMAL')
            if alert_level == 'NORMAL':
                return
            
            severity_map = {
                'CAUTION': AlertSeverity.CAUTION.value,
                'WARNING': AlertSeverity.WARNING.value,
                'CRITICAL': AlertSeverity.CRITICAL.value,
                'EMERGENCY': AlertSeverity.EMERGENCY.value
            }
            severity = severity_map.get(alert_level, AlertSeverity.WARNING.value)
            
            alert = {
                "agent_id": self.agent_id,
                "severity": severity,
                "alert_level": alert_level,
                "timestamp": logic_output.get('timestamp'),
                "message": self._build_alert_message(logic_output),
                "data": {
                    "threat_level": logic_output.get('threat_level'),
                    "anomaly_score": logic_output.get('anomaly_score'),
                    "consecutive_anomalies": logic_output.get('consecutive_anomalies'),
                    "action": logic_output.get('action')
                }
            }
            
            routed_channels = self.router.route_alert(alert)
            if self.mqtt_client:
                await self._publish_mqtt_alert(alert)
            
            logger.info(f"Alert routed: {alert_level} -> {routed_channels}")
        except Exception as e:
            logger.error(f"Error handling alerts: {e}", exc_info=True)
    
    def _build_alert_message(self, logic_output: Dict[str, Any]) -> str:
        """Build human-readable alert message."""
        alert_level = logic_output.get('alert_level', 'UNKNOWN')
        threat_level = logic_output.get('threat_level', 'UNKNOWN')
        anomaly_score = logic_output.get('anomaly_score', 0.0)
        return f"[{alert_level}] Cyber Threat Alert - Threat: {threat_level}, Anomaly Score: {anomaly_score:.2f}"
    
    async def _publish_mqtt_alert(self, alert: Dict[str, Any]) -> None:
        """Publish alert to MQTT topic."""
        try:
            mqtt_channels = [ch for ch in self.config.get('channels', []) if ch.get('type') == 'mqtt']
            if mqtt_channels:
                topic = mqtt_channels[0].get('topic', f'alerts/{self.agent_id}')
                if self.mqtt_client and self.mqtt_client.connected:
                    success = self.mqtt_client.publish(topic, alert, qos=1)
                    if success:
                        logger.debug(f"Alert published to MQTT topic: {topic}")
        except Exception as e:
            logger.error(f"Error publishing MQTT alert: {e}", exc_info=True)


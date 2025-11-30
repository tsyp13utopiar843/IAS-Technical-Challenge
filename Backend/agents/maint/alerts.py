"""
PM Agent Alerts Component
Handles alert routing to multiple channels based on severity.
"""
import logging
from typing import Dict, Any, Optional

from agents.utils.alert_router import AlertRouter, AlertSeverity

logger = logging.getLogger("PMAgent.Alerts")


class PMAlerts:
    """
    Predictive Maintenance Alerts Component.
    
    Routes alerts to configured channels (MQTT, Email, SMS, Database, Webhook, SCADA)
    based on severity levels.
    """
    
    def __init__(self, agent_id: str, config: Dict[str, Any], mqtt_client: Optional[Any] = None):
        """
        Initialize alerts component.
        
        Args:
            agent_id: Agent identifier
            config: Alert configuration
            mqtt_client: MQTT client for publishing alerts (optional)
        """
        self.agent_id = agent_id
        self.config = config
        self.mqtt_client = mqtt_client
        
        # Initialize alert router
        self.router = AlertRouter(config)
        
        logger.info(f"Initialized PM Alerts (channels: {len(config.get('channels', []))})")
    
    async def handle_alerts(self, logic_output: Dict[str, Any]) -> None:
        """
        Trigger alerts and actions based on logic output.
        
        Args:
            logic_output: Output from logic component with alert_level, action, etc.
        """
        try:
            alert_level = logic_output.get('alert_level', 'NORMAL')
            
            # Only send alerts for non-normal conditions
            if alert_level == 'NORMAL':
                return
            
            # Map alert level to severity
            severity_map = {
                'CAUTION': AlertSeverity.CAUTION.value,
                'WARNING': AlertSeverity.WARNING.value,
                'CRITICAL': AlertSeverity.CRITICAL.value,
                'EMERGENCY': AlertSeverity.EMERGENCY.value
            }
            severity = severity_map.get(alert_level, AlertSeverity.WARNING.value)
            
            # Build alert message
            alert = {
                "agent_id": self.agent_id,
                "severity": severity,
                "alert_level": alert_level,
                "timestamp": logic_output.get('timestamp'),
                "message": self._build_alert_message(logic_output),
                "data": {
                    "rul_hours": logic_output.get('rul_hours'),
                    "health_score": logic_output.get('health_score'),
                    "failure_probability": logic_output.get('failure_probability'),
                    "action": logic_output.get('action'),
                    "recommended_action": logic_output.get('recommended_action'),
                    "priority": logic_output.get('priority')
                }
            }
            
            # Route alert
            routed_channels = self.router.route_alert(alert)
            
            # Publish to MQTT if client available
            if self.mqtt_client:
                await self._publish_mqtt_alert(alert)
            
            logger.info(f"Alert routed: {alert_level} -> {routed_channels}")
            
        except Exception as e:
            logger.error(f"Error handling alerts: {e}", exc_info=True)
    
    def _build_alert_message(self, logic_output: Dict[str, Any]) -> str:
        """
        Build human-readable alert message.
        
        Args:
            logic_output: Logic component output
            
        Returns:
            Alert message string
        """
        alert_level = logic_output.get('alert_level', 'UNKNOWN')
        rul_hours = logic_output.get('rul_hours', 0.0)
        action = logic_output.get('action', 'UNKNOWN')
        recommended = logic_output.get('recommended_action', '')
        
        return (f"[{alert_level}] Predictive Maintenance Alert - "
                f"RUL: {rul_hours:.1f} hours, Action: {action}. {recommended}")
    
    async def _publish_mqtt_alert(self, alert: Dict[str, Any]) -> None:
        """Publish alert to MQTT topic."""
        try:
            # Find MQTT channel config
            mqtt_channels = [ch for ch in self.config.get('channels', []) if ch.get('type') == 'mqtt']
            
            if mqtt_channels:
                topic = mqtt_channels[0].get('topic', f'alerts/{self.agent_id}')
                
                if self.mqtt_client and self.mqtt_client.connected:
                    success = self.mqtt_client.publish(topic, alert, qos=1)
                    if success:
                        logger.debug(f"Alert published to MQTT topic: {topic}")
                    else:
                        logger.warning(f"Failed to publish alert to MQTT topic: {topic}")
        except Exception as e:
            logger.error(f"Error publishing MQTT alert: {e}", exc_info=True)


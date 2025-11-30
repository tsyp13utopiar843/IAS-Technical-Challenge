"""
Backlog Agent Alerts Component
Handles notifications when backlogs are generated.
"""
import logging
from typing import Dict, Any, Optional

from agents.utils.alert_router import AlertRouter, AlertSeverity

logger = logging.getLogger("BacklogAgent.Alerts")


class BacklogAlerts:
    """Backlog Generation Alerts Component."""
    
    def __init__(self, agent_id: str, config: Dict[str, Any], mqtt_client: Optional[Any] = None):
        """Initialize alerts component."""
        self.agent_id = agent_id
        self.config = config
        self.mqtt_client = mqtt_client
        self.router = AlertRouter(config) if config.get('channels') else None
        logger.info(f"Initialized Backlog Alerts")
    
    async def handle_backlog_generated(self, backlog: Dict[str, Any]) -> None:
        """
        Handle backlog generation notification.
        
        Args:
            backlog: Generated backlog dictionary
        """
        try:
            # Only send alerts for critical shifts
            shift_status = backlog.get('statistics', {}).get('shift_status', 'NORMAL')
            if shift_status not in ['CRITICAL', 'WARNING']:
                return
            
            severity = AlertSeverity.CRITICAL.value if shift_status == 'CRITICAL' else AlertSeverity.WARNING.value
            
            alert = {
                "agent_id": self.agent_id,
                "severity": severity,
                "alert_level": shift_status,
                "timestamp": backlog.get('generated_at'),
                "message": f"Shift backlog generated: {backlog.get('summary', '')}",
                "data": {
                    "backlog_id": backlog.get('backlog_id'),
                    "total_violations": backlog.get('total_violations', 0),
                    "total_anomalies": backlog.get('total_anomalies', 0),
                    "priority_items_count": len(backlog.get('priority_items', []))
                }
            }
            
            if self.router:
                routed_channels = self.router.route_alert(alert)
                logger.info(f"Backlog alert routed: {shift_status} -> {routed_channels}")
            
            if self.mqtt_client:
                await self._publish_mqtt_alert(alert)
            
        except Exception as e:
            logger.error(f"Error handling backlog alert: {e}", exc_info=True)
    
    async def _publish_mqtt_alert(self, alert: Dict[str, Any]) -> None:
        """Publish alert to MQTT topic."""
        try:
            if self.mqtt_client and self.mqtt_client.connected:
                topic = f"alerts/{self.agent_id}"
                success = self.mqtt_client.publish(topic, alert, qos=1)
                if success:
                    logger.debug(f"Backlog alert published to MQTT topic: {topic}")
        except Exception as e:
            logger.error(f"Error publishing MQTT alert: {e}", exc_info=True)


"""
Alert Router Utility
Routes alerts to different channels based on configuration.
"""
from typing import Dict, Any, List
from enum import Enum
import logging
import json

logger = logging.getLogger("AlertRouter")


class AlertSeverity(Enum):
    """Alert severity levels."""
    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class AlertChannel(Enum):
    """Alert delivery channels."""
    MQTT = "mqtt"
    EMAIL = "email"
    SMS = "sms"
    DATABASE = "database"
    WEBHOOK = "webhook"
    SCADA = "scada"


class AlertRouter:
    """Routes alerts to configured channels based on severity."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize alert router.
        
        Args:
            config: Alert configuration with channel definitions
        """
        self.config = config
        self.channels = self._parse_channels(config.get('channels', []))
    
    def _parse_channels(self, channel_configs: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        Parse channel configurations.
        
        Args:
            channel_configs: List of channel configurations
        
        Returns:
            Dictionary mapping channel types to configs
        """
        channels = {}
        
        for channel_config in channel_configs:
            channel_type = channel_config.get('type')
            if channel_type not in channels:
                channels[channel_type] = []
            channels[channel_type].append(channel_config)
        
        return channels
    
    def route_alert(self, alert: Dict[str, Any]) -> List[str]:
        """
        Route alert to appropriate channels.
        
        Args:
            alert: Alert dictionary with severity, message, etc.
        
        Returns:
            List of channels that received the alert
        """
        severity = alert.get('severity', AlertSeverity.NORMAL.value)
        routed_channels = []
        
        for channel_type, channel_configs in self.channels.items():
            for channel_config in channel_configs:
                # Check if this channel should receive this severity
                allowed_severities = channel_config.get('severity', [])
                
                if not allowed_severities or severity in allowed_severities:
                    try:
                        self._send_to_channel(channel_type, channel_config, alert)
                        routed_channels.append(channel_type)
                    except Exception as e:
                        logger.error(f"Failed to send alert to {channel_type}: {e}")
        
        return routed_channels
    
    def _send_to_channel(self, channel_type: str, config: Dict[str, Any], alert: Dict[str, Any]) -> None:
        """
        Send alert to specific channel.
        
        Args:
            channel_type: Type of channel
            config: Channel configuration
            alert: Alert to send
        """
        if channel_type == "mqtt":
            self._send_mqtt(config, alert)
        elif channel_type == "email":
            self._send_email(config, alert)
        elif channel_type == "sms":
            self._send_sms(config, alert)
        elif channel_type == "database":
            self._send_database(config, alert)
        elif channel_type == "webhook":
            self._send_webhook(config, alert)
        elif channel_type == "scada":
            self._send_scada(config, alert)
        else:
            logger.warning(f"Unknown channel type: {channel_type}")
    
    def _send_mqtt(self, config: Dict[str, Any], alert: Dict[str, Any]) -> None:
        """Send alert via MQTT."""
        topic = config.get('topic', 'alerts/default')
        # Note: Actual MQTT publishing would be done via MQTTClientWrapper
        # This is a placeholder for the routing logic
        logger.info(f"Routing alert to MQTT topic: {topic}")
        # mqtt_client.publish(topic, alert)
    
    def _send_email(self, config: Dict[str, Any], alert: Dict[str, Any]) -> None:
        """Send alert via email."""
        recipients = config.get('recipients', [])
        logger.info(f"Routing alert to email recipients: {recipients}")
        # TODO: Implement email sending (SMTP)
    
    def _send_sms(self, config: Dict[str, Any], alert: Dict[str, Any]) -> None:
        """Send alert via SMS."""
        recipients = config.get('recipients', [])
        logger.info(f"Routing alert to SMS recipients: {recipients}")
        # TODO: Implement SMS sending (Twilio, AWS SNS, etc.)
    
    def _send_database(self, config: Dict[str, Any], alert: Dict[str, Any]) -> None:
        """Log alert to database."""
        logger.info(f"Logging alert to database")
        # TODO: Implement database logging
    
    def _send_webhook(self, config: Dict[str, Any], alert: Dict[str, Any]) -> None:
        """Send alert to webhook."""
        url = config.get('url')
        logger.info(f"Sending alert to webhook: {url}")
        # TODO: Implement HTTP POST to webhook
    
    def _send_scada(self, config: Dict[str, Any], alert: Dict[str, Any]) -> None:
        """Send alert to SCADA system."""
        logger.info(f"Routing alert to SCADA system")
        # TODO: Implement SCADA alarm triggering

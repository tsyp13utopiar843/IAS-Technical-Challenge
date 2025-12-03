import os
import logging
from typing import Optional

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


logger = logging.getLogger("6G-MAS-Notifier")


class NotificationManager:
    """
    Simple Twilio-based notification manager.

    This replaces SMTP/Slack-style alerting with SMS (or WhatsApp if the
    Twilio number is configured for it).
    """

    def __init__(self) -> None:
        self.account_sid: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_number: Optional[str] = os.getenv("TWILIO_FROM_NUMBER")
        self.to_number: Optional[str] = os.getenv("TWILIO_TO_NUMBER")

        if not all(
            [self.account_sid, self.auth_token, self.from_number, self.to_number]
        ):
            logger.warning(
                "Twilio credentials missing. SMS alerts will be disabled. "
                "Expected TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, "
                "TWILIO_FROM_NUMBER, TWILIO_TO_NUMBER."
            )
            self.client: Optional[Client] = None
        else:
            self.client = Client(self.account_sid, self.auth_token)

    async def send_alert(self, severity: str, message: str, source_agent: str) -> None:
        """
        Sends an SMS alert via Twilio.

        Args:
            severity: Severity level string (e.g., CRITICAL, WARNING).
            message: Human-readable description of the issue.
            source_agent: Identifier for the originating agent.
        """
        if not self.client:
            logger.error("Cannot send alert: Twilio client not initialized.")
            return

        emoji = "🔴" if severity.upper() == "CRITICAL" else "⚠️"
        body = f"{emoji} [6G-MAS ALERT] {severity}\nAgent: {source_agent}\nMsg: {message}"

        try:
            twilio_message = self.client.messages.create(
                body=body,
                from_=self.from_number,
                to=self.to_number,
            )
            logger.info(f"Twilio SMS sent: {twilio_message.sid}")
        except TwilioRestException as exc:
            logger.error(f"Failed to send Twilio SMS: {exc}")


# Singleton instance to be imported by agents/orchestrator
notifier = NotificationManager()



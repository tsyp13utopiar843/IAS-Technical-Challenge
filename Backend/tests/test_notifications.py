import os
from types import SimpleNamespace

import pytest

from agents.utils import notifications


def test_notifier_disabled_when_env_missing(monkeypatch):
    """If Twilio env vars are missing, client should be None and send_alert should be a no-op."""
    # Clear env vars
    for key in [
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_FROM_NUMBER",
        "TWILIO_TO_NUMBER",
    ]:
        monkeypatch.delenv(key, raising=False)

    # Recreate manager to re-evaluate env
    manager = notifications.NotificationManager()

    assert manager.client is None


@pytest.mark.asyncio
async def test_send_alert_uses_twilio_client(monkeypatch):
    """send_alert should call Twilio client when properly configured."""

    # Set env vars
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "auth-token")
    monkeypatch.setenv("TWILIO_FROM_NUMBER", "+10000000000")
    monkeypatch.setenv("TWILIO_TO_NUMBER", "+19999999999")

    called = {}

    class FakeMessages:
        def create(self, body, from_, to):
            called["body"] = body
            called["from_"] = from_
            called["to"] = to
            return SimpleNamespace(sid="SM123")

    class FakeClient:
        def __init__(self, sid, token):
            self.sid = sid
            self.token = token
            self.messages = FakeMessages()

    # Patch Client in module
    monkeypatch.setattr(notifications, "Client", FakeClient)

    manager = notifications.NotificationManager()
    assert isinstance(manager.client, FakeClient)

    await manager.send_alert(
        severity="CRITICAL",
        message="Something went wrong",
        source_agent="test-agent",
    )

    assert called["from_"] == "+10000000000"
    assert called["to"] == "+19999999999"
    assert "[6G-MAS ALERT]" in called["body"]



import datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from agents.orchestrator.main import app, Alert, system_state


class DummyAsyncResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


class DummyAsyncClient:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, json):
        # Return a simple plan response
        return DummyAsyncResponse({"action": "TEST_ACTION"})


@pytest.fixture
def client():
    return TestClient(app)


def test_status_endpoint(client):
    resp = client.get("/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent"] == "Orchestrator"


@pytest.mark.asyncio
async def test_alert_triggers_planner_and_updates_state(monkeypatch):
    # Patch httpx.AsyncClient used inside the route
    import agents.orchestrator.main as main_mod

    monkeypatch.setattr(main_mod, "httpx", SimpleNamespace(AsyncClient=DummyAsyncClient))

    # Spy for notifier
    calls = {}

    async def fake_send_alert(severity, message, source_agent):
        calls["severity"] = severity
        calls["message"] = message
        calls["source_agent"] = source_agent

    monkeypatch.setattr(main_mod.notifier, "send_alert", fake_send_alert)

    alert = Alert(
        level="CRITICAL",
        type="TEST",
        source="test-agent",
        details="Something happened",
    )

    # Call the route function directly
    result = await main_mod.receive_alert(alert)

    assert result["status"] == "handled"
    assert result["action"] == "TEST_ACTION"

    # Ensure system_state updated
    assert len(system_state["alerts"]) >= 1
    assert system_state["alerts"][0]["details"] == "Something happened"

    # Twilio notifier called for CRITICAL level
    assert calls["severity"] == "CRITICAL"
    assert calls["source_agent"] == "test-agent"



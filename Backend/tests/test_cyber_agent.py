import pytest

import agents.cyber.main as cyber_main


class FakeCyberModel:
    def __init__(self, *args, **kwargs):
        self.loaded = False

    def load_model(self):
        self.loaded = True

    def preprocess(self, raw_data):
        return {"preprocessed": True, "raw": raw_data}

    def predict(self, preprocessed):
        return {"threat_level": "HIGH", "is_anomaly": True}


class FakeCyberLogic:
    def __init__(self, *args, **kwargs):
        pass

    def apply_logic(self, prediction):
        return {"alert_level": "CRITICAL", "action": "ISOLATE"}


class FakeCyberState:
    def __init__(self, *args, **kwargs):
        self.updated = False

    def update(self, prediction, logic_output, success=True):
        self.updated = True
        self.last_prediction = prediction
        self.last_logic_output = logic_output

    def get_state(self):
        return {"updated": self.updated}

    async def start_checkpointing(self):
        return None

    async def stop_checkpointing(self):
        return None


class FakeCyberComm:
    def __init__(self, *args, **kwargs):
        self.predictions = []
        self.mqtt_client = object()

    async def start_communication(self):
        return None

    async def stop_communication(self):
        return None

    async def publish_prediction(self, prediction):
        self.predictions.append(prediction)


class FakeCyberAlerts:
    def __init__(self, *args, **kwargs):
        self.alerts = []

    async def handle_alerts(self, logic_output):
        self.alerts.append(logic_output)


@pytest.mark.asyncio
async def test_cyber_agent_process_sensor_data(monkeypatch):
    monkeypatch.setattr(cyber_main, "CyberModel", FakeCyberModel)
    monkeypatch.setattr(cyber_main, "CyberLogic", FakeCyberLogic)
    monkeypatch.setattr(cyber_main, "CyberState", FakeCyberState)
    monkeypatch.setattr(cyber_main, "CyberCommunication", FakeCyberComm)
    monkeypatch.setattr(cyber_main, "CyberAlerts", FakeCyberAlerts)

    config = {
        "agent": {"id": "cyber_agent_test"},
        "model": {},
        "logic": {"thresholds": {}},
        "state": {},
        "communication": {},
        "alerts": {},
    }

    agent = cyber_main.CyberAgent(config)

    payload = {"sensor": "latency", "value": 123.0}
    await agent._process_sensor_data(payload)

    assert agent.state.updated is True
    assert len(agent.communication.predictions) == 1
    combined = agent.communication.predictions[0]
    assert combined["threat_level"] == "HIGH"
    assert combined["alert_level"] == "CRITICAL"
    assert len(agent.alerts.alerts) == 1



import pytest

import agents.safety.main as safety_main


class FakeHazardModel:
    def __init__(self, *args, **kwargs):
        self.loaded = False

    def load_model(self):
        self.loaded = True

    def preprocess(self, raw_data):
        return {"preprocessed": True, "raw": raw_data}

    def predict(self, preprocessed):
        return {
            "hazard_score": 0.8,
            "hazard_type": "FALL",
            "safety_score": 60.0,
        }


class FakeHazardLogic:
    def __init__(self, *args, **kwargs):
        pass

    def apply_logic(self, prediction):
        return {"alert_level": "WARNING", "action": "INSPECT"}


class FakeHazardState:
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


class FakeHazardComm:
    def __init__(self, *args, **kwargs):
        self.predictions = []
        self.mqtt_client = object()

    async def start_communication(self):
        return None

    async def stop_communication(self):
        return None

    async def publish_prediction(self, prediction):
        self.predictions.append(prediction)


class FakeHazardAlerts:
    def __init__(self, *args, **kwargs):
        self.alerts = []

    async def handle_alerts(self, logic_output):
        self.alerts.append(logic_output)


@pytest.mark.asyncio
async def test_safety_agent_process_sensor_data(monkeypatch):
    monkeypatch.setattr(safety_main, "HazardModel", FakeHazardModel)
    monkeypatch.setattr(safety_main, "HazardLogic", FakeHazardLogic)
    monkeypatch.setattr(safety_main, "HazardState", FakeHazardState)
    monkeypatch.setattr(safety_main, "HazardCommunication", FakeHazardComm)
    monkeypatch.setattr(safety_main, "HazardAlerts", FakeHazardAlerts)

    config = {
        "agent": {"id": "hazard_agent_test"},
        "model": {},
        "logic": {"thresholds": {}},
        "state": {},
        "communication": {},
        "alerts": {},
    }

    agent = safety_main.HazardAgent(config)

    payload = {"sensor": "camera", "value": "frame-data"}
    await agent._process_sensor_data(payload)

    assert agent.state.updated is True
    assert len(agent.communication.predictions) == 1
    combined = agent.communication.predictions[0]
    assert combined["hazard_type"] == "FALL"
    assert combined["alert_level"] == "WARNING"
    assert len(agent.alerts.alerts) == 1



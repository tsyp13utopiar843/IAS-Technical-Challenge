import pytest

import agents.maint.main as pm_main


class FakeModel:
    def __init__(self, *args, **kwargs):
        self.loaded = False

    def load_model(self):
        self.loaded = True

    def preprocess(self, raw_data):
        # Return sentinel to indicate preprocessing happened
        return {"preprocessed": True, "raw": raw_data}

    def predict(self, preprocessed):
        assert preprocessed["preprocessed"] is True
        return {"rul_hours": 10.0, "health_score": 95.0}


class FakeLogic:
    def __init__(self, *args, **kwargs):
        pass

    def apply_logic(self, prediction):
        # Simple mapping based on RUL
        return {"alert_level": "NORMAL", "action": "MONITOR"}


class FakeState:
    def __init__(self, *args, **kwargs):
        self.updated = False

    def update(self, prediction, logic_output, success=True):
        self.updated = True
        self.last_success = success
        self.last_prediction = prediction
        self.last_logic_output = logic_output

    def get_state(self):
        return {"updated": self.updated}

    async def start_checkpointing(self):
        return None

    async def stop_checkpointing(self):
        return None

    def save_state(self, path):
        self.saved_path = path

    def load_state(self, path):
        self.loaded_path = path


class FakeComm:
    def __init__(self, *args, **kwargs):
        self.predictions = []
        self.mqtt_client = object()

    async def start_communication(self):
        return None

    async def stop_communication(self):
        return None

    async def publish_prediction(self, prediction):
        self.predictions.append(prediction)


class FakeAlerts:
    def __init__(self, *args, **kwargs):
        self.alerts = []

    async def handle_alerts(self, logic_output):
        self.alerts.append(logic_output)


@pytest.mark.asyncio
async def test_pm_agent_process_sensor_data(monkeypatch):
    # Patch heavy components with fakes
    monkeypatch.setattr(pm_main, "PMModel", FakeModel)
    monkeypatch.setattr(pm_main, "PMLogic", FakeLogic)
    monkeypatch.setattr(pm_main, "PMState", FakeState)
    monkeypatch.setattr(pm_main, "PMCommunication", FakeComm)
    monkeypatch.setattr(pm_main, "PMAlerts", FakeAlerts)

    config = {
        "agent": {"id": "pm_agent_test"},
        "model": {},
        "logic": {"thresholds": {}},
        "state": {},
        "communication": {},
        "alerts": {},
    }

    agent = pm_main.PMAgent(config)

    # Sanity: components replaced by our fakes
    assert isinstance(agent.model, FakeModel)
    assert isinstance(agent.logic, FakeLogic)
    assert isinstance(agent.state, FakeState)
    assert isinstance(agent.communication, FakeComm)
    assert isinstance(agent.alerts, FakeAlerts)

    sensor_payload = {"sensor": "vibration", "value": 1.23}

    await agent._process_sensor_data(sensor_payload)

    # State was updated
    assert agent.state.updated is True

    # A combined prediction was published
    assert len(agent.communication.predictions) == 1
    combined = agent.communication.predictions[0]
    assert combined["rul_hours"] == 10.0
    assert combined["alert_level"] == "NORMAL"

    # Alerts handler called
    assert len(agent.alerts.alerts) == 1
    assert agent.alerts.alerts[0]["alert_level"] == "NORMAL"



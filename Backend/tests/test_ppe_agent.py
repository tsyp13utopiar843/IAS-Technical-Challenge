import pytest

import agents.ppe.main as ppe_main


class FakePPEModel:
    def __init__(self, *args, **kwargs):
        self.loaded = False

    def load_model(self):
        self.loaded = True

    def preprocess(self, raw_data):
        return {"preprocessed": True, "raw": raw_data}

    def predict(self, preprocessed):
        return {
            "compliance_rate": 85.0,
            "overall_compliance": "PARTIAL",
        }


class FakePPELogic:
    def __init__(self, *args, **kwargs):
        pass

    def apply_logic(self, prediction):
        return {"alert_level": "INFO", "action": "LOG"}


class FakePPEState:
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


class FakePPEComm:
    def __init__(self, *args, **kwargs):
        self.predictions = []
        self.mqtt_client = object()

    async def start_communication(self):
        return None

    async def stop_communication(self):
        return None

    async def publish_prediction(self, prediction):
        self.predictions.append(prediction)


class FakePPEAlerts:
    def __init__(self, *args, **kwargs):
        self.alerts = []

    async def handle_alerts(self, logic_output):
        self.alerts.append(logic_output)


@pytest.mark.asyncio
async def test_ppe_agent_process_sensor_data(monkeypatch):
    monkeypatch.setattr(ppe_main, "PPEModel", FakePPEModel)
    monkeypatch.setattr(ppe_main, "PPELogic", FakePPELogic)
    monkeypatch.setattr(ppe_main, "PPEState", FakePPEState)
    monkeypatch.setattr(ppe_main, "PPECommunication", FakePPEComm)
    monkeypatch.setattr(ppe_main, "PPEAlerts", FakePPEAlerts)

    config = {
        "agent": {"id": "ppe_agent_test"},
        "model": {},
        "logic": {"thresholds": {}},
        "state": {},
        "communication": {},
        "alerts": {},
    }

    agent = ppe_main.PPEAgent(config)

    payload = {"sensor": "camera", "value": "frame-data", "worker_id": "W123"}
    await agent._process_sensor_data(payload)

    assert agent.state.updated is True
    assert len(agent.communication.predictions) == 1
    combined = agent.communication.predictions[0]
    assert combined["compliance_rate"] == 85.0
    assert combined["overall_compliance"] == "PARTIAL"
    assert combined["worker_id"] == "W123"
    assert len(agent.alerts.alerts) == 1



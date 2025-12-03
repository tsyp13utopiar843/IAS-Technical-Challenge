import pytest

import agents.energy.main as energy_main


class FakeEnergyModel:
    def __init__(self, *args, **kwargs):
        self.loaded = False

    def load_model(self):
        self.loaded = True

    def preprocess(self, raw_data):
        return {"preprocessed": True, "raw": raw_data}

    def predict(self, preprocessed):
        return {"consumption_kwh": 100.0, "efficiency_score": 90.0}


class FakeEnergyLogic:
    def __init__(self, *args, **kwargs):
        pass

    def apply_logic(self, prediction):
        return {"alert_level": "CAUTION", "action": "OPTIMIZE"}


class FakeEnergyState:
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


class FakeEnergyComm:
    def __init__(self, *args, **kwargs):
        self.predictions = []
        self.mqtt_client = object()

    async def start_communication(self):
        return None

    async def stop_communication(self):
        return None

    async def publish_prediction(self, prediction):
        self.predictions.append(prediction)


class FakeEnergyAlerts:
    def __init__(self, *args, **kwargs):
        self.alerts = []

    async def handle_alerts(self, logic_output):
        self.alerts.append(logic_output)


@pytest.mark.asyncio
async def test_energy_agent_process_sensor_data(monkeypatch):
    monkeypatch.setattr(energy_main, "EnergyModel", FakeEnergyModel)
    monkeypatch.setattr(energy_main, "EnergyLogic", FakeEnergyLogic)
    monkeypatch.setattr(energy_main, "EnergyState", FakeEnergyState)
    monkeypatch.setattr(energy_main, "EnergyCommunication", FakeEnergyComm)
    monkeypatch.setattr(energy_main, "EnergyAlerts", FakeEnergyAlerts)

    config = {
        "agent": {"id": "energy_agent_test"},
        "model": {},
        "logic": {"thresholds": {}},
        "state": {},
        "communication": {},
        "alerts": {},
    }

    agent = energy_main.EnergyAgent(config)

    payload = {"sensor": "power", "value": 42.0}
    await agent._process_sensor_data(payload)

    assert agent.state.updated is True
    assert len(agent.communication.predictions) == 1
    combined = agent.communication.predictions[0]
    assert combined["consumption_kwh"] == 100.0
    assert combined["alert_level"] == "CAUTION"
    assert len(agent.alerts.alerts) == 1



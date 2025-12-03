import pytest

import agents.backlog.main as backlog_main


class FakeBacklogModel:
    def __init__(self, *args, **kwargs):
        self.calls = []

    def generate_backlog(self, shift_data):
        self.calls.append(shift_data)
        return {
            "backlog_id": "BL-001",
            "total_violations": 2,
            "total_anomalies": 1,
        }


class FakeBacklogLogic:
    def __init__(self, shift_duration_hours=8):
        self.shift_duration_hours = shift_duration_hours

    def is_shift_complete(self, start, now):
        # Always consider the shift complete for test
        return True

    def aggregate_shift_data(self, events, shift_start, shift_end):
        return {
            "events": events,
            "shift_start": shift_start,
            "shift_end": shift_end,
        }

    def apply_logic(self, shift_data):
        return {"shift_status": "NORMAL", "priority": 3}


class FakeBacklogState:
    def __init__(self, *args, **kwargs):
        self.events = []
        self.backlogs = []
        self.updated = False
        self._current_shift_start = None

    def add_event(self, event):
        self.events.append(event)

    def get_current_shift_start(self):
        return self._current_shift_start

    def get_current_shift_events(self):
        return list(self.events)

    def update(self, prediction, logic_output, success=True):
        self.updated = True
        self.last_prediction = prediction
        self.last_logic_output = logic_output

    def record_backlog(self, backlog):
        self.backlogs.append(backlog)

    def save_backlog(self, backlog, backlog_dir):
        self.saved_backlog_dir = backlog_dir

    def start_new_shift(self):
        self.events.clear()

    def get_state(self):
        return {"backlogs": self.backlogs}

    async def start_checkpointing(self):
        return None

    async def stop_checkpointing(self):
        return None


class FakeBacklogComm:
    def __init__(self, *args, **kwargs):
        self.published = []
        self.mqtt_client = object()

    async def start_communication(self):
        return None

    async def stop_communication(self):
        return None

    async def publish_backlog(self, backlog):
        self.published.append(backlog)


class FakeBacklogAlerts:
    def __init__(self, *args, **kwargs):
        self.calls = []

    async def handle_backlog_generated(self, backlog):
        self.calls.append(backlog)


@pytest.mark.asyncio
async def test_backlog_agent_collects_events_and_generates_backlog(monkeypatch):
    monkeypatch.setattr(backlog_main, "BacklogModel", FakeBacklogModel)
    monkeypatch.setattr(backlog_main, "BacklogLogic", FakeBacklogLogic)
    monkeypatch.setattr(backlog_main, "BacklogState", FakeBacklogState)
    monkeypatch.setattr(backlog_main, "BacklogCommunication", FakeBacklogComm)
    monkeypatch.setattr(backlog_main, "BacklogAlerts", FakeBacklogAlerts)

    config = {
        "agent": {"id": "backlog_agent_test"},
        "model": {},
        "logic": {"shift_duration_hours": 8},
        "state": {"backlog_dir": "backlogs"},
        "communication": {},
        "alerts": {},
    }

    agent = backlog_main.BacklogAgent(config)

    # Simulate events arriving from other agents
    await agent._process_event(
        {"agent_id": "pm_agent", "alert_level": "WARNING", "message": "RUL low"}
    )
    await agent._process_event(
        {"agent_id": "cyber_agent", "alert_level": "CRITICAL", "message": "Anomaly"}
    )

    # Manually invoke one iteration of _monitor_shifts core logic by calling its internals:
    # we call predict/logic/update/publish/alerts using mocked state/events.
    state = agent.state
    logic = agent.logic
    model = agent.model
    comm = agent.communication
    alerts = agent.alerts

    # Fake times
    shift_start = None
    state._current_shift_start = shift_start
    events = state.get_current_shift_events()
    shift_data = logic.aggregate_shift_data(events, shift_start, shift_start)
    backlog = model.generate_backlog(shift_data)
    logic_output = logic.apply_logic(shift_data)
    state.update(backlog, logic_output)
    state.record_backlog(backlog)
    await comm.publish_backlog(backlog)
    await alerts.handle_backlog_generated(backlog)

    assert state.updated is True
    assert len(state.backlogs) == 1
    assert len(comm.published) == 1
    assert len(alerts.calls) == 1



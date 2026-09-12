import pytest
from app.agents.gip import gip_bus, GIPEvent, GIPEventBus
from app.services.outcome_service import OutcomeEngine, OutcomeLifecycleStatus


def test_gip_event_bus():
    events = []
    gip_bus.subscribe(lambda e: events.append(e))
    event = gip_bus.publish("LEAD_CREATED", "ai-lead-intelligence", "task-1", {"lead_id": "lead-1"})
    assert event.event_type == "LEAD_CREATED"
    assert len(events) == 1
    assert events[0].payload["lead_id"] == "lead-1"


def test_outcome_lifecycle_transitions():
    assert OutcomeEngine.transition("REQUESTED", "PLANNED") is True
    assert OutcomeEngine.transition("REQUESTED", "AUTHORIZED") is False
    assert OutcomeEngine.transition("PLANNED", "AUTHORIZED") is True
    assert OutcomeEngine.transition("EXECUTING", "EXECUTED") is True
    assert OutcomeEngine.transition("EXECUTING", "VERIFIED") is False


def test_outcome_record():
    result = OutcomeEngine.record("lead", "lead-1", "success", "success", {"value": 100})
    assert result["lifecycle_status"] == "OUTCOME_RECORDED"
    assert result["technical_status"] == "success"
    assert result["business_status"] == "success"

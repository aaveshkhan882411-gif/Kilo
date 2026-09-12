import pytest
from app.services.outcome_service import OutcomeEngine, OutcomeLifecycleStatus


def test_outcome_lifecycle_validation():
    assert OutcomeEngine.transition("REQUESTED", "PLANNED") is True
    assert OutcomeEngine.transition("PLANNED", "AUTHORIZED") is True
    assert OutcomeEngine.transition("AUTHORIZED", "EXECUTING") is True
    assert OutcomeEngine.transition("EXECUTING", "EXECUTED") is True
    assert OutcomeEngine.transition("EXECUTED", "VERIFIED") is True
    assert OutcomeEngine.transition("VERIFIED", "OUTCOME_RECORDED") is True


def test_invalid_transitions():
    assert OutcomeEngine.transition("REQUESTED", "EXECUTING") is False
    assert OutcomeEngine.transition("EXECUTED", "PLANNED") is False
    assert OutcomeEngine.transition("OUTCOME_RECORDED", "REQUESTED") is False


def test_outcome_record():
    result = OutcomeEngine.record(
        entity_type="lead",
        entity_id="lead-123",
        technical_status="success",
        business_status="success",
        data={"value": 100},
    )
    assert result["lifecycle_status"] == "OUTCOME_RECORDED"
    assert result["technical_status"] == "success"
    assert result["business_status"] == "success"
    assert "timestamp" in result

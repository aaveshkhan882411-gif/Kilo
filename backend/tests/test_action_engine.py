import pytest
from app.services.action_service import ActionEngine, ActionStatus


def test_action_plan_creation():
    plan = {"action": "create_lead", "params": {"name": "John Doe", "email": "john@example.com"}}
    assert plan["action"] == "create_lead"


@pytest.mark.asyncio
async def test_action_execution():
    engine = ActionEngine()
    plan = {"action": "send_email", "params": {"to": "test@example.com", "subject": "Hello"}}
    result = await engine.execute_plan(plan, {})
    assert result["status"] == ActionStatus.OUTCOME.value
    assert result["result"]["success"] is True


def test_action_engine_status_enum():
    assert ActionStatus.AI_DECISION.value == "AI_DECISION"
    assert ActionStatus.OUTCOME.value == "OUTCOME"

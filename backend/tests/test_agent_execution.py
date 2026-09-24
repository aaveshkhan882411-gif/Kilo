import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import create_access_token
from app.models.organization import Organization
from app.models.user import User


def headers_for(user: User):
    token = create_access_token(
        data={
            "sub": user.id,
            "org_id": user.org_id,
        }
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_agent_execution_validates_contract_permissions(
    client: TestClient,
    db: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    response = client.post(
        "/api/agents/agents/ai-sales/execute",
        headers=headers_for(test_user),
        json={
            "task_id": "task-1",
            "agent_id": "ai-sales",
            "org_id": test_org.id,
            "input": {"lead_id": "lead-1"},
            "context": {},
            "permissions": [
                "read_crm",
                "write_deals",
                "send_email",
            ],
            "authorization_required": False,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["agent_id"] == "ai-sales"
    assert body["task_id"] == "task-1"
    assert body["status"] == "failed"
    assert body["result"]["status"] == "no_tool_requested"


@pytest.mark.asyncio
async def test_agent_execution_rejects_missing_permissions(
    client: TestClient,
    db: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    response = client.post(
        "/api/agents/agents/ai-sales/execute",
        headers=headers_for(test_user),
        json={
            "task_id": "task-2",
            "agent_id": "ai-sales",
            "org_id": test_org.id,
            "input": {},
            "context": {},
            "permissions": ["read_crm"],
            "authorization_required": False,
        },
    )

    assert response.status_code == 403
    assert "send_email" in response.json()["detail"]["missing_permissions"]


@pytest.mark.asyncio
async def test_agent_execution_rejects_cross_tenant_task(
    client: TestClient,
    db: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    response = client.post(
        "/api/agents/agents/ai-sales/execute",
        headers=headers_for(test_user),
        json={
            "task_id": "task-3",
            "agent_id": "ai-sales",
            "org_id": "different-org-id",
            "input": {},
            "context": {},
            "permissions": [
                "read_crm",
                "write_deals",
                "send_email",
            ],
            "authorization_required": False,
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_agent_execution_rejects_unknown_agent(
    client: TestClient,
    db: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    response = client.post(
        "/api/agents/agents/not-a-real-agent/execute",
        headers=headers_for(test_user),
        json={
            "task_id": "task-4",
            "agent_id": "not-a-real-agent",
            "org_id": test_org.id,
            "input": {},
            "context": {},
            "permissions": [],
            "authorization_required": False,
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_agent_execution_runs_registered_tool_with_authenticated_tenant_context(
    client: TestClient,
    db: AsyncSession,
    test_org: Organization,
    test_user: User,
):
    from app.agents.base import BaseAgent
    from app.agents.registry import registry
    from app.agents.tool_registry import tool_registry

    captured = {}

    async def fake_crm_tool(params):
        captured.update(params["_execution_context"])
        return {
            "success": True,
            "status": "executed",
        }

    tool_registry.register("crm", fake_crm_tool)

    original_agent = registry.get("ai-sales")

    class TestSalesAgent(BaseAgent):
        async def create_plan(self, context):
            return {
                "plan": ["execute crm"],
                "requested_tool": "crm",
                "parameters": {},
            }

    registry.register(TestSalesAgent("ai-sales", "AI Sales"))

    try:
        response = client.post(
            "/api/agents/agents/ai-sales/execute",
            headers=headers_for(test_user),
            json={
                "task_id": "task-router-tool-1",
                "agent_id": "ai-sales",
                "org_id": test_org.id,
                "input": {},
                "context": {
                    "org_id": "attacker-controlled-org",
                    "user_id": "attacker-controlled-user",
                },
                "permissions": [
                    "read_crm",
                    "write_deals",
                    "send_email",
                ],
                "authorization_required": False,
            },
        )

        assert response.status_code == 200
        body = response.json()

        assert body["status"] == "completed"
        assert body["result"]["success"] is True
        assert captured["org_id"] == test_user.org_id
        assert captured["user_id"] == test_user.id

    finally:
        if original_agent is not None:
            registry.register(original_agent)


@pytest.mark.asyncio
async def test_base_agent_reason_calls_model_router(monkeypatch):
    from app.agents.base import BaseAgent
    from app.ai.router import ModelRouter

    agent = BaseAgent("ai-sales", "AI Sales")
    captured = {}

    async def fake_complete(
        prompt,
        agent_id=None,
        model=None,
        max_tokens=1024,
        temperature=0.7,
        context=None,
    ):
        captured["prompt"] = prompt
        captured["agent_id"] = agent_id
        captured["max_tokens"] = max_tokens
        captured["temperature"] = temperature
        captured["context"] = context

        return {
            "text": '{"reasoning":"use CRM","requested_tool":"crm","parameters":{}}',
            "model": "test-model",
            "tokens_used": 12,
        }

    monkeypatch.setattr(ModelRouter, "complete", fake_complete)

    result = await agent.reason(
        {
            "input": {"lead_id": "lead-1"},
            "org_id": "attacker-org",
            "user_id": "attacker-user",
            "permissions": ["read_crm"],
        }
    )

    assert result["model_response"]
    assert captured["agent_id"] == "ai-sales"
    assert captured["max_tokens"] == 1024
    assert captured["temperature"] == 0.2

    assert captured["context"]["agent"]["id"] == "ai-sales"
    assert "crm" in captured["context"]["contract"]["allowed_tools"]
    assert "read_crm" in captured["context"]["contract"]["required_permissions"]

    # Security-sensitive runtime values must not be forwarded to the model context.
    assert "org_id" not in captured["context"]
    assert "user_id" not in captured["context"]
    assert "permissions" not in captured["context"]


@pytest.mark.asyncio
async def test_base_agent_create_plan_parses_valid_json():
    from app.agents.base import BaseAgent

    agent = BaseAgent("ai-sales", "AI Sales")

    result = await agent.create_plan(
        {
            "model_response": (
                '{"reasoning":"use crm",'
                '"requested_tool":"crm",'
                '"parameters":{"lead_id":"lead-1"}}'
            )
        }
    )

    assert result["requested_tool"] == "crm"
    assert result["parameters"] == {"lead_id": "lead-1"}
    assert result["reasoning"] == "use crm"


@pytest.mark.asyncio
async def test_base_agent_create_plan_parses_fenced_json():
    from app.agents.base import BaseAgent

    agent = BaseAgent("ai-sales", "AI Sales")

    result = await agent.create_plan(
        {
            "model_response": """```json
{"reasoning":"use crm","requested_tool":"crm","parameters":{"lead_id":"lead-1"}}
```"""
        }
    )

    assert result["requested_tool"] == "crm"
    assert result["parameters"] == {"lead_id": "lead-1"}


@pytest.mark.asyncio
async def test_base_agent_create_plan_rejects_malformed_json():
    from app.agents.base import BaseAgent

    agent = BaseAgent("ai-sales", "AI Sales")

    result = await agent.create_plan(
        {
            "model_response": "this is not json"
        }
    )

    assert result["requested_tool"] is None
    assert result["parameters"] == {}


@pytest.mark.asyncio
async def test_base_agent_create_plan_rejects_disallowed_tool():
    from app.agents.base import BaseAgent

    agent = BaseAgent("ai-sales", "AI Sales")

    result = await agent.create_plan(
        {
            "model_response": (
                '{"reasoning":"attack",'
                '"requested_tool":"database",'
                '"parameters":{"query":"secret"}}'
            )
        }
    )

    assert result["requested_tool"] is None
    assert result["parameters"] == {}


@pytest.mark.asyncio
async def test_base_agent_create_plan_strips_security_parameters():
    from app.agents.base import BaseAgent

    agent = BaseAgent("ai-sales", "AI Sales")

    result = await agent.create_plan(
        {
            "model_response": (
                '{"reasoning":"crm",'
                '"requested_tool":"crm",'
                '"parameters":{'
                '"lead_id":"lead-1",'
                '"org_id":"attacker-org",'
                '"user_id":"attacker-user",'
                '"permissions":["read_all"],'
                '"authorization":"true",'
                '"access_token":"secret",'
                '"token":"secret",'
                '"api_key":"secret"'
                '}}'
            )
        }
    )

    assert result["requested_tool"] == "crm"
    assert result["parameters"] == {"lead_id": "lead-1"}


@pytest.mark.asyncio
async def test_base_agent_reason_handles_model_failure(monkeypatch):
    from app.agents.base import BaseAgent
    from app.ai.router import ModelRouter

    agent = BaseAgent("ai-sales", "AI Sales")

    async def fake_complete(*args, **kwargs):
        return {
            "error": "vllm_connection_error",
            "provider": "vllm",
        }

    monkeypatch.setattr(ModelRouter, "complete", fake_complete)

    result = await agent.reason({"input": {"lead_id": "lead-1"}})

    assert result["error"] == "vllm_connection_error"
    assert result["model_response"] == ""

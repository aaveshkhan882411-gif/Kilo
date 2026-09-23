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

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
    assert body["status"] == "validated"


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

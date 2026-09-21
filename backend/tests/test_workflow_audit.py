import pytest
from sqlalchemy import select

from app.models import AuditLog


@pytest.mark.asyncio
async def test_create_workflow_creates_audit_log(
    client,
    auth_headers,
    db,
    test_user,
):
    response = client.post(
        "/api/workflows/",
        headers=auth_headers,
        json={
            "name": "Audit Workflow",
            "trigger_type": "lead_created",
            "actions": [{"type": "notify", "channel": "email"}],
            "is_active": True,
        },
    )

    assert response.status_code == 201
    workflow = response.json()

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "CREATE",
            AuditLog.entity_type == "workflow",
            AuditLog.entity_id == workflow["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["name"] == "Audit Workflow"
    assert audit_log.changes["trigger_type"] == "lead_created"
    assert audit_log.changes["actions"][0]["type"] == "notify"
    assert audit_log.changes["is_active"] is True

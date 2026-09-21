import pytest
from sqlalchemy import select

from app.models import AuditLog


@pytest.mark.asyncio
async def test_create_task_creates_audit_log(
    client,
    auth_headers,
    db,
    test_user,
):
    response = client.post(
        "/api/tasks/tasks",
        headers=auth_headers,
        json={
            "title": "Audit Task",
            "description": "Task audit integration test",
            "status": "pending",
            "priority": "high",
        },
    )

    assert response.status_code == 201
    task = response.json()

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "CREATE",
            AuditLog.entity_type == "task",
            AuditLog.entity_id == task["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["title"] == "Audit Task"
    assert audit_log.changes["status"] == "pending"
    assert audit_log.changes["priority"] == "high"

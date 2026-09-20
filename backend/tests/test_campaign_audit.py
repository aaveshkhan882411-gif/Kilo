import pytest
from sqlalchemy import select

from app.models import AuditLog


@pytest.mark.asyncio
async def test_create_campaign_creates_audit_log(
    client,
    auth_headers,
    db,
    test_user,
):
    response = client.post(
        "/api/campaigns/",
        headers=auth_headers,
        json={
            "name": "Audit Campaign",
            "type": "email",
            "status": "draft",
            "budget": 1000,
        },
    )

    assert response.status_code == 201
    campaign = response.json()

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "CREATE",
            AuditLog.entity_type == "campaign",
            AuditLog.entity_id == campaign["id"],
        )
    )

    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["name"] == "Audit Campaign"
    assert audit_log.changes["type"] == "email"
    assert audit_log.changes["status"] == "draft"
    assert audit_log.changes["budget"] == 1000

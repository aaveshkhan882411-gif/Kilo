import pytest
from sqlalchemy import select

from app.models import AuditLog


@pytest.mark.asyncio
async def test_create_appointment_creates_audit_log(
    client,
    auth_headers,
    db,
    test_user,
):
    response = client.post(
        "/api/appointments/",
        headers=auth_headers,
        json={
            "title": "Audit Appointment",
            "description": "Appointment audit integration test",
            "start_time": "2030-01-15T10:00:00",
            "end_time": "2030-01-15T11:00:00",
            "location": "Test Office",
            "organizer_id": test_user.id,
            "status": "scheduled",
        },
    )

    assert response.status_code == 201
    appointment = response.json()

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "CREATE",
            AuditLog.entity_type == "appointment",
            AuditLog.entity_id == appointment["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["title"] == "Audit Appointment"
    assert audit_log.changes["organizer_id"] == test_user.id
    assert audit_log.changes["status"] == "scheduled"

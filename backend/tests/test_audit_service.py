import pytest
from sqlalchemy import select

from app.models import AuditLog, Lead
from app.services.audit_service import AuditService


@pytest.mark.asyncio
async def test_audit_service_records_log(db, test_org, test_user):
    audit_log = await AuditService.record(
        db=db,
        org_id=test_org.id,
        user_id=test_user.id,
        action="CREATE",
        entity_type="lead",
        entity_id="lead-123",
        changes={"status": "new"},
        ip_address="127.0.0.1",
        user_agent="pytest",
    )

    assert audit_log.id is not None
    assert audit_log.org_id == test_org.id
    assert audit_log.user_id == test_user.id
    assert audit_log.action == "CREATE"
    assert audit_log.entity_type == "lead"
    assert audit_log.entity_id == "lead-123"
    assert audit_log.changes == {"status": "new"}
    assert audit_log.ip_address == "127.0.0.1"
    assert audit_log.user_agent == "pytest"
    assert audit_log.created_at is not None

    result = await db.execute(
        select(AuditLog).where(AuditLog.id == audit_log.id)
    )
    saved_log = result.scalar_one()

    assert saved_log.org_id == test_org.id
    assert saved_log.action == "CREATE"
    assert saved_log.entity_type == "lead"


@pytest.mark.asyncio
async def test_create_lead_creates_audit_log(client, auth_headers, db, test_user):
    response = client.post(
        "/api/leads/",
        headers=auth_headers,
        json={
            "first_name": "Audit",
            "last_name": "Lead",
            "email": "audit-lead@example.com",
            "phone": "9999999999",
            "company": "Audit Test",
            "source": "test",
            "notes": "audit integration test",
        },
    )

    assert response.status_code == 201
    lead = response.json()

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "CREATE",
            AuditLog.entity_type == "lead",
            AuditLog.entity_id == lead["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["first_name"] == "Audit"
    assert audit_log.changes["email"] == "audit-lead@example.com"


@pytest.mark.asyncio
async def test_update_lead_creates_audit_log(client, auth_headers, db, test_user):
    create_response = client.post(
        "/api/leads/",
        headers=auth_headers,
        json={
            "first_name": "Before",
            "last_name": "Update",
            "email": "update-audit@example.com",
        },
    )

    assert create_response.status_code == 201
    lead = create_response.json()

    update_response = client.patch(
        f"/api/leads/{lead['id']}",
        headers=auth_headers,
        json={
            "first_name": "After",
            "company": "Updated Company",
        },
    )

    assert update_response.status_code == 200
    updated_lead = update_response.json()
    assert updated_lead["first_name"] == "After"
    assert updated_lead["company"] == "Updated Company"

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "UPDATE",
            AuditLog.entity_type == "lead",
            AuditLog.entity_id == lead["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["first_name"]["old"] == "Before"
    assert audit_log.changes["first_name"]["new"] == "After"
    assert audit_log.changes["company"]["old"] is None
    assert audit_log.changes["company"]["new"] == "Updated Company"


@pytest.mark.asyncio
async def test_delete_lead_creates_audit_log(client, auth_headers, db, test_user):
    create_response = client.post(
        "/api/leads/",
        headers=auth_headers,
        json={
            "first_name": "Delete",
            "last_name": "Audit",
            "email": "delete-audit@example.com",
            "company": "Delete Test",
        },
    )

    assert create_response.status_code == 201
    lead = create_response.json()

    delete_response = client.delete(
        f"/api/leads/{lead['id']}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 204

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "DELETE",
            AuditLog.entity_type == "lead",
            AuditLog.entity_id == lead["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["first_name"] == "Delete"
    assert audit_log.changes["email"] == "delete-audit@example.com"
    assert audit_log.changes["company"] == "Delete Test"

    result = await db.execute(
        select(Lead).where(Lead.id == lead["id"])
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_score_lead_creates_audit_log(client, auth_headers, db, test_user):
    create_response = client.post(
        "/api/leads/",
        headers=auth_headers,
        json={
            "first_name": "Score",
            "last_name": "Audit",
            "email": "score-audit@example.com",
            "phone": "9999999999",
            "company": "Score Test",
        },
    )

    assert create_response.status_code == 201
    lead = create_response.json()

    score_response = client.post(
        f"/api/leads/{lead['id']}/score",
        headers=auth_headers,
    )

    assert score_response.status_code == 200
    scored = score_response.json()
    assert scored["lead_id"] == lead["id"]
    assert scored["score"] == 85

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "SCORE",
            AuditLog.entity_type == "lead",
            AuditLog.entity_id == lead["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["score"]["old"] == 0
    assert audit_log.changes["score"]["new"] == 85
    assert audit_log.changes["reasoning"] == "Automated scoring"


@pytest.mark.asyncio
async def test_qualify_lead_creates_audit_log(client, auth_headers, db, test_user):
    create_response = client.post(
        "/api/leads/",
        headers=auth_headers,
        json={
            "first_name": "Qualify",
            "last_name": "Audit",
            "email": "qualify-audit@example.com",
        },
    )

    assert create_response.status_code == 201
    lead = create_response.json()

    qualify_response = client.post(
        f"/api/leads/{lead['id']}/qualify",
        headers=auth_headers,
    )

    assert qualify_response.status_code == 200
    qualified = qualify_response.json()
    assert qualified["status"] == "qualified"
    assert qualified["score"] == 20

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "QUALIFY",
            AuditLog.entity_type == "lead",
            AuditLog.entity_id == lead["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["status"]["old"] == "new"
    assert audit_log.changes["status"]["new"] == "qualified"
    assert audit_log.changes["score"]["old"] == 0
    assert audit_log.changes["score"]["new"] == 20

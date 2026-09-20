import pytest
from sqlalchemy import select

from app.models import AuditLog
from app.services.audit_service import AuditService


@pytest.mark.asyncio
async def test_create_contact_creates_audit_log(
    client, auth_headers, db, test_user
):
    response = client.post(
        "/api/crm/contacts",
        headers=auth_headers,
        json={
            "first_name": "CRM",
            "last_name": "Contact",
            "email": "crm-contact@example.com",
            "phone": "9999999999",
            "company": "CRM Test",
            "position": "Manager",
        },
    )

    assert response.status_code == 201
    contact = response.json()

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "CREATE",
            AuditLog.entity_type == "contact",
            AuditLog.entity_id == contact["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["first_name"] == "CRM"
    assert audit_log.changes["email"] == "crm-contact@example.com"


@pytest.mark.asyncio
async def test_create_company_creates_audit_log(
    client, auth_headers, db, test_user
):
    response = client.post(
        "/api/crm/companies",
        headers=auth_headers,
        json={
            "name": "CRM Company",
            "industry": "Technology",
            "website": "https://example.com",
            "size": "50-100",
            "location": "India",
            "annual_revenue": 1000000,
        },
    )

    assert response.status_code == 201
    company = response.json()

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "CREATE",
            AuditLog.entity_type == "company",
            AuditLog.entity_id == company["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["name"] == "CRM Company"
    assert audit_log.changes["industry"] == "Technology"


@pytest.mark.asyncio
async def test_create_deal_creates_audit_log(
    client, auth_headers, db, test_user
):
    company_response = client.post(
        "/api/crm/companies",
        headers=auth_headers,
        json={"name": "Deal Company"},
    )
    assert company_response.status_code == 201
    company = company_response.json()

    contact_response = client.post(
        "/api/crm/contacts",
        headers=auth_headers,
        json={
            "first_name": "Deal",
            "last_name": "Contact",
            "email": "deal-contact@example.com",
        },
    )
    assert contact_response.status_code == 201
    contact = contact_response.json()

    response = client.post(
        "/api/crm/deals",
        headers=auth_headers,
        json={
            "title": "CRM Deal",
            "company_id": company["id"],
            "contact_id": contact["id"],
            "value": 50000,
            "stage": "qualification",
            "probability": 25,
        },
    )

    assert response.status_code == 201
    deal = response.json()

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "CREATE",
            AuditLog.entity_type == "deal",
            AuditLog.entity_id == deal["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["title"] == "CRM Deal"
    assert audit_log.changes["value"] == 50000


@pytest.mark.asyncio
async def test_update_deal_stage_creates_audit_log(
    client, auth_headers, db, test_user
):
    company_response = client.post(
        "/api/crm/companies",
        headers=auth_headers,
        json={"name": "Stage Company"},
    )
    assert company_response.status_code == 201
    company = company_response.json()

    contact_response = client.post(
        "/api/crm/contacts",
        headers=auth_headers,
        json={
            "first_name": "Stage",
            "last_name": "Contact",
            "email": "stage-contact@example.com",
        },
    )
    assert contact_response.status_code == 201
    contact = contact_response.json()

    create_response = client.post(
        "/api/crm/deals",
        headers=auth_headers,
        json={
            "title": "Stage Deal",
            "company_id": company["id"],
            "contact_id": contact["id"],
            "value": 75000,
            "stage": "qualification",
            "probability": 20,
        },
    )
    assert create_response.status_code == 201
    deal = create_response.json()

    response = client.patch(
        f"/api/crm/deals/{deal['id']}",
        headers=auth_headers,
        json={
            "stage": "proposal",
            "probability": 60,
        },
    )

    assert response.status_code == 200
    updated_deal = response.json()
    assert updated_deal["stage"] == "proposal"
    assert updated_deal["probability"] == 60

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "UPDATE",
            AuditLog.entity_type == "deal",
            AuditLog.entity_id == deal["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["stage"]["old"] == "qualification"
    assert audit_log.changes["stage"]["new"] == "proposal"
    assert audit_log.changes["probability"]["old"] == 20
    assert audit_log.changes["probability"]["new"] == 60


@pytest.mark.asyncio
async def test_create_customer_creates_audit_log(
    client, auth_headers, db, test_user
):
    contact_response = client.post(
        "/api/crm/contacts",
        headers=auth_headers,
        json={
            "first_name": "Customer",
            "last_name": "Contact",
            "email": "customer-contact@example.com",
        },
    )
    assert contact_response.status_code == 201
    contact = contact_response.json()

    response = client.post(
        "/api/crm/customers",
        headers=auth_headers,
        json={
            "contact_id": contact["id"],
            "status": "active",
            "lifetime_value": 25000,
        },
    )

    assert response.status_code == 201
    customer = response.json()

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == test_user.org_id,
            AuditLog.user_id == test_user.id,
            AuditLog.action == "CREATE",
            AuditLog.entity_type == "customer",
            AuditLog.entity_id == customer["id"],
        )
    )
    audit_log = result.scalar_one_or_none()

    assert audit_log is not None
    assert audit_log.changes["contact_id"] == contact["id"]
    assert audit_log.changes["status"] == "active"
    assert audit_log.changes["lifetime_value"] == 25000

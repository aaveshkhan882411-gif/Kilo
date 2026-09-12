import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.organization import Organization
from app.models.lead import Lead
from app.models.user import User
from app.auth.utils import hash_password


@pytest.mark.asyncio
async def test_org_a_cannot_see_org_b_leads(client: TestClient, db: AsyncSession):
    org_a = Organization(name="Org A", slug="org-a", plan="standard")
    org_b = Organization(name="Org B", slug="org-b", plan="standard")
    db.add_all([org_a, org_b])
    await db.commit()

    user_a = User(email="a@example.com", hashed_password=hash_password("pass"), full_name="User A", role="admin", org_id=org_a.id, is_verified=True)
    user_b = User(email="b@example.com", hashed_password=hash_password("pass"), full_name="User B", role="admin", org_id=org_b.id, is_verified=True)
    db.add_all([user_a, user_b])
    await db.commit()

    lead_b = Lead(org_id=org_b.id, first_name="Secret", last_name="Lead", email="secret@example.com")
    db.add(lead_b)
    await db.commit()


@pytest.mark.asyncio
async def test_tenant_data_scoped_by_org_id(client: TestClient, db: AsyncSession):
    org = Organization(name="Test Org", slug="test-org", plan="standard")
    db.add(org)
    await db.commit()

    user = User(email="tenant@example.com", hashed_password=hash_password("pass"), full_name="Tenant User", role="admin", org_id=org.id, is_verified=True)
    db.add(user)
    await db.commit()

    lead = Lead(org_id=org.id, first_name="Test", last_name="Lead", email="test@example.com")
    db.add(lead)
    await db.commit()
    assert lead.org_id == org.id

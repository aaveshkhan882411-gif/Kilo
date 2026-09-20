import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.lead import Lead
from app.models.user import User
from app.auth.utils import hash_password, create_access_token


@pytest.mark.asyncio
async def test_org_a_cannot_see_org_b_leads(client: TestClient, db: AsyncSession):
    org_a = Organization(name="Org A", slug="org-a", plan="standard")
    org_b = Organization(name="Org B", slug="org-b", plan="standard")
    db.add_all([org_a, org_b])
    await db.commit()

    user_a = User(
        email="a@example.com",
        hashed_password=hash_password("pass"),
        full_name="User A",
        role="admin",
        org_id=org_a.id,
        is_verified=True,
    )
    lead_b = Lead(
        org_id=org_b.id,
        first_name="Secret",
        last_name="Lead",
        email="secret@example.com",
    )
    db.add_all([user_a, lead_b])
    await db.commit()

    token = create_access_token(
        data={"sub": user_a.id, "org_id": org_a.id}
    )

    response = client.get(
        "/api/leads/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert all(
        item["email"] != "secret@example.com"
        for item in response.json()
    )


@pytest.mark.asyncio
async def test_tenant_data_scoped_by_org_id(
    client: TestClient,
    db: AsyncSession,
):
    org = Organization(
        name="Test Org",
        slug="test-org",
        plan="standard",
    )
    db.add(org)
    await db.commit()

    user = User(
        email="tenant@example.com",
        hashed_password=hash_password("pass"),
        full_name="Tenant User",
        role="admin",
        org_id=org.id,
        is_verified=True,
    )
    db.add(user)
    await db.commit()

    lead = Lead(
        org_id=org.id,
        first_name="Test",
        last_name="Lead",
        email="test@example.com",
    )
    db.add(lead)
    await db.commit()

    assert lead.org_id == org.id


@pytest.mark.asyncio
async def test_org_a_cannot_read_or_modify_org_b(
    client: TestClient,
    db: AsyncSession,
):
    org_a = Organization(
        name="Org A",
        slug="org-a",
        plan="standard",
    )
    org_b = Organization(
        name="Org B",
        slug="org-b",
        plan="standard",
    )
    db.add_all([org_a, org_b])
    await db.commit()

    user_a = User(
        email="org-a-user@example.com",
        hashed_password=hash_password("pass"),
        full_name="Org A User",
        role="admin",
        org_id=org_a.id,
        is_verified=True,
    )
    db.add(user_a)
    await db.commit()

    token = create_access_token(
        data={"sub": user_a.id, "org_id": org_a.id}
    )
    headers = {"Authorization": f"Bearer {token}"}

    get_response = client.get(
        f"/api/organizations/{org_b.id}",
        headers=headers,
    )

    assert get_response.status_code in (403, 404)

    patch_response = client.patch(
        f"/api/organizations/{org_b.id}",
        headers=headers,
        json={"name": "HACKED"},
    )

    assert patch_response.status_code in (403, 404)

@pytest.mark.asyncio
async def test_admin_cannot_create_user_in_another_org(client: TestClient, db: AsyncSession):
    org_a = Organization(name="Create Org A", slug="create-org-a", plan="standard")
    org_b = Organization(name="Create Org B", slug="create-org-b", plan="standard")
    db.add_all([org_a, org_b])
    await db.commit()

    admin_a = User(
        email="admin-create-a@example.com",
        hashed_password=hash_password("pass"),
        full_name="Admin A",
        role="admin",
        org_id=org_a.id,
        is_verified=True,
    )
    db.add(admin_a)
    await db.commit()

    token = create_access_token(
        data={"sub": admin_a.id, "org_id": org_a.id}
    )

    response = client.post(
        "/api/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "cross-org-user@example.com",
            "password": "StrongPassword123!",
            "full_name": "Cross Org User",
            "role": "viewer",
            "org_id": org_b.id,
        },
    )

    assert response.status_code == 201
    created = response.json()

    assert created["org_id"] == org_a.id
    assert created["org_id"] != org_b.id


@pytest.mark.asyncio
async def test_admin_cannot_create_privileged_user(
    client: TestClient,
    db: AsyncSession,
):
    org = Organization(
        name="Role Create Org",
        slug="role-create-org",
        plan="standard",
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)

    admin = User(
        email="role-admin@example.com",
        hashed_password=hash_password("pass"),
        full_name="Role Admin",
        role="admin",
        org_id=org.id,
        is_verified=True,
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    token = create_access_token(
        data={"sub": admin.id, "org_id": org.id}
    )

    response = client.post(
        "/api/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "privileged-user@example.com",
            "password": "StrongPassword123!",
            "full_name": "Privileged User",
            "role": "owner",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_cannot_promote_user_to_admin(
    client: TestClient,
    db: AsyncSession,
):
    org = Organization(
        name="Role Update Org",
        slug="role-update-org",
        plan="standard",
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)

    admin = User(
        email="update-admin@example.com",
        hashed_password=hash_password("pass"),
        full_name="Update Admin",
        role="admin",
        org_id=org.id,
        is_verified=True,
    )

    viewer = User(
        email="update-viewer@example.com",
        hashed_password=hash_password("pass"),
        full_name="Update Viewer",
        role="viewer",
        org_id=org.id,
        is_verified=True,
    )

    db.add_all([admin, viewer])
    await db.commit()
    await db.refresh(admin)
    await db.refresh(viewer)

    token = create_access_token(
        data={"sub": admin.id, "org_id": org.id}
    )

    response = client.patch(
        f"/api/users/{viewer.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": "admin"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_owner_can_create_admin(
    client: TestClient,
    db: AsyncSession,
):
    org = Organization(
        name="Owner Role Org",
        slug="owner-role-org",
        plan="standard",
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)

    owner = User(
        email="role-owner@example.com",
        hashed_password=hash_password("pass"),
        full_name="Role Owner",
        role="owner",
        org_id=org.id,
        is_verified=True,
    )
    db.add(owner)
    await db.commit()
    await db.refresh(owner)

    token = create_access_token(
        data={"sub": owner.id, "org_id": org.id}
    )

    response = client.post(
        "/api/users/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "email": "new-admin@example.com",
            "password": "StrongPassword123!",
            "full_name": "New Admin",
            "role": "admin",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "admin"


@pytest.mark.asyncio
async def test_owner_cannot_change_owner_role(
    client: TestClient,
    db: AsyncSession,
):
    org = Organization(
        name="Owner Protection Org",
        slug="owner-protection-org",
        plan="standard",
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)

    owner = User(
        email="owner-protection@example.com",
        hashed_password=hash_password("pass"),
        full_name="Protected Owner",
        role="owner",
        org_id=org.id,
        is_verified=True,
    )
    db.add(owner)
    await db.commit()
    await db.refresh(owner)

    token = create_access_token(
        data={"sub": owner.id, "org_id": org.id}
    )

    response = client.patch(
        f"/api/users/{owner.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": "admin"},
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_org_a_cannot_see_org_b_integrations(
    client: TestClient,
    db: AsyncSession,
):
    from app.models import Integration

    org_a = Organization(
        name="Integration Org A",
        slug="integration-org-a",
        plan="standard",
    )
    org_b = Organization(
        name="Integration Org B",
        slug="integration-org-b",
        plan="standard",
    )
    db.add_all([org_a, org_b])
    await db.commit()

    user_a = User(
        email="integration-a@example.com",
        hashed_password=hash_password("pass"),
        full_name="Integration User A",
        role="admin",
        org_id=org_a.id,
        is_verified=True,
    )
    integration_b = Integration(
        org_id=org_b.id,
        provider="secret-provider",
        config={"secret": "org-b-secret"},
        status="active",
    )
    db.add_all([user_a, integration_b])
    await db.commit()
    await db.refresh(integration_b)

    token = create_access_token(
        data={"sub": user_a.id, "org_id": org_a.id}
    )

    response = client.get(
        "/api/integrations/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert all(
        item["id"] != integration_b.id
        for item in response.json()
    )


@pytest.mark.asyncio
async def test_org_a_cannot_update_org_b_integration(
    client: TestClient,
    db: AsyncSession,
):
    from app.models import Integration

    org_a = Organization(
        name="Integration Update A",
        slug="integration-update-a",
        plan="standard",
    )
    org_b = Organization(
        name="Integration Update B",
        slug="integration-update-b",
        plan="standard",
    )
    db.add_all([org_a, org_b])
    await db.commit()

    user_a = User(
        email="integration-update-a@example.com",
        hashed_password=hash_password("pass"),
        full_name="Integration Update User A",
        role="admin",
        org_id=org_a.id,
        is_verified=True,
    )
    integration_b = Integration(
        org_id=org_b.id,
        provider="protected-provider",
        config={"protected": True},
        status="active",
    )
    db.add_all([user_a, integration_b])
    await db.commit()
    await db.refresh(integration_b)

    token = create_access_token(
        data={"sub": user_a.id, "org_id": org_a.id}
    )

    response = client.patch(
        f"/api/integrations/{integration_b.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "inactive"},
    )

    assert response.status_code == 404

    await db.refresh(integration_b)
    assert integration_b.status == "active"


@pytest.mark.asyncio
async def test_org_a_cannot_see_org_b_outcomes(
    client: TestClient,
    db: AsyncSession,
):
    from app.models import Outcome

    org_a = Organization(
        name="Outcome Org A",
        slug="outcome-org-a",
        plan="standard",
    )
    org_b = Organization(
        name="Outcome Org B",
        slug="outcome-org-b",
        plan="standard",
    )
    db.add_all([org_a, org_b])
    await db.commit()

    user_a = User(
        email="outcome-a@example.com",
        hashed_password=hash_password("pass"),
        full_name="Outcome User A",
        role="admin",
        org_id=org_a.id,
        is_verified=True,
    )
    outcome_b = Outcome(
        org_id=org_b.id,
        entity_type="lead",
        entity_id="org-b-lead-001",
        lifecycle_status="REQUESTED",
        technical_status="pending",
        business_status="pending",
        data={"secret": "org-b-data"},
    )
    db.add_all([user_a, outcome_b])
    await db.commit()
    await db.refresh(outcome_b)

    token = create_access_token(
        data={"sub": user_a.id, "org_id": org_a.id}
    )

    response = client.get(
        "/api/outcomes/lead/org-b-lead-001",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert all(
        item["id"] != outcome_b.id
        for item in response.json()
    )


@pytest.mark.asyncio
async def test_org_a_cannot_update_org_b_outcome(
    client: TestClient,
    db: AsyncSession,
):
    from app.models import Outcome

    org_a = Organization(
        name="Outcome Update A",
        slug="outcome-update-a",
        plan="standard",
    )
    org_b = Organization(
        name="Outcome Update B",
        slug="outcome-update-b",
        plan="standard",
    )
    db.add_all([org_a, org_b])
    await db.commit()

    user_a = User(
        email="outcome-update-a@example.com",
        hashed_password=hash_password("pass"),
        full_name="Outcome Update User A",
        role="admin",
        org_id=org_a.id,
        is_verified=True,
    )
    outcome_b = Outcome(
        org_id=org_b.id,
        entity_type="lead",
        entity_id="org-b-lead-update-001",
        lifecycle_status="REQUESTED",
        technical_status="pending",
        business_status="pending",
        data={"protected": True},
    )
    db.add_all([user_a, outcome_b])
    await db.commit()
    await db.refresh(outcome_b)

    token = create_access_token(
        data={"sub": user_a.id, "org_id": org_a.id}
    )

    response = client.patch(
        f"/api/outcomes/{outcome_b.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "lifecycle_status": "COMPLETED",
            "technical_status": "success",
            "business_status": "won",
            "data": {"hacked": True},
        },
    )

    assert response.status_code == 404

    await db.refresh(outcome_b)
    assert outcome_b.lifecycle_status == "REQUESTED"
    assert outcome_b.technical_status == "pending"
    assert outcome_b.business_status == "pending"
    assert outcome_b.data == {"protected": True}

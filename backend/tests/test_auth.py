import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.organization import Organization
from app.models.user import User
from app.auth.utils import hash_password


@pytest.mark.asyncio
async def test_user_registration(client: TestClient, db: AsyncSession):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepass123",
            "full_name": "New User",
            "organization_name": "Registration Test Org",
            "organization_slug": "registration-test-org",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "newuser@example.com"
    assert data["role"] == "owner"
    assert data["org_id"]

    org = await db.get(Organization, data["org_id"])

    assert org is not None
    assert org.name == "Registration Test Org"
    assert org.slug == "registration-test-org"
    assert org.plan == "starter"


@pytest.mark.asyncio
async def test_login_success(client: TestClient, db: AsyncSession):
    org = Organization(
        name="Test",
        slug="test",
        plan="standard",
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)

    user = User(
        email="login@example.com",
        hashed_password=hash_password("password123"),
        full_name="Login User",
        role="admin",
        org_id=org.id,
        is_verified=True,
    )
    db.add(user)
    await db.commit()

    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure(client: TestClient):
    response = client.post(
        "/api/auth/login",
        json={
            "email": "wrong@example.com",
            "password": "wrongpass",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_registration_cannot_control_role_or_org(client: TestClient, db: AsyncSession):
    org = Organization(
        name="Protected Org",
        slug="protected-org",
        plan="standard",
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)

    response = client.post(
        "/api/auth/register",
        json={
            "email": "attacker@example.com",
            "password": "securepass123",
            "full_name": "Attacker",
            "organization_name": "Attacker Org",
            "organization_slug": "attacker-org",
            "role": "admin",
            "org_id": org.id,
        },
    )

    assert response.status_code == 422

    result = await db.execute(
        select(User).where(User.email == "attacker@example.com")
    )
    assert result.scalar_one_or_none() is None

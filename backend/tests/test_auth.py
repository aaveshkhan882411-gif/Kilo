import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.organization import Organization
from app.models import AuthSession
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


@pytest.mark.asyncio
async def test_refresh_rotates_token_and_revokes_old_session(
    client: TestClient,
    db: AsyncSession,
):
    org = Organization(
        name="Refresh Test Org",
        slug="refresh-test-org",
        plan="standard",
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)

    user = User(
        email="refresh@example.com",
        hashed_password=hash_password("password123"),
        full_name="Refresh User",
        role="admin",
        org_id=org.id,
        is_verified=True,
    )
    db.add(user)
    await db.commit()

    login = client.post(
        "/api/auth/login",
        json={
            "email": "refresh@example.com",
            "password": "password123",
        },
    )

    assert login.status_code == 200

    login_data = login.json()
    old_refresh_token = login_data["refresh_token"]

    old_session_result = await db.execute(
        select(AuthSession).where(
            AuthSession.user_id == user.id,
        )
    )
    old_session = old_session_result.scalar_one()

    assert old_session.revoked_at is None
    assert old_session.token_hash != old_refresh_token

    refresh = client.post(
        "/api/auth/refresh",
        json={
            "refresh_token": old_refresh_token,
        },
    )

    assert refresh.status_code == 200

    refresh_data = refresh.json()
    new_refresh_token = refresh_data["refresh_token"]

    assert new_refresh_token
    assert new_refresh_token != old_refresh_token

    await db.refresh(old_session)

    assert old_session.revoked_at is not None

    new_session_result = await db.execute(
        select(AuthSession).where(
            AuthSession.user_id == user.id,
            AuthSession.revoked_at.is_(None),
        )
    )
    new_session = new_session_result.scalar_one()

    assert new_session.id != old_session.id
    assert new_session.token_hash != old_session.token_hash

    old_refresh_again = client.post(
        "/api/auth/refresh",
        json={
            "refresh_token": old_refresh_token,
        },
    )

    assert old_refresh_again.status_code == 401

    new_refresh = client.post(
        "/api/auth/refresh",
        json={
            "refresh_token": new_refresh_token,
        },
    )

    assert new_refresh.status_code == 200


@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(
    client: TestClient,
    db: AsyncSession,
):
    org = Organization(
        name="Logout Test Org",
        slug="logout-test-org",
        plan="standard",
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)

    user = User(
        email="logout@example.com",
        hashed_password=hash_password("password123"),
        full_name="Logout User",
        role="admin",
        org_id=org.id,
        is_verified=True,
    )
    db.add(user)
    await db.commit()

    login = client.post(
        "/api/auth/login",
        json={
            "email": "logout@example.com",
            "password": "password123",
        },
    )

    assert login.status_code == 200

    refresh_token = login.json()["refresh_token"]

    logout = client.post(
        "/api/auth/logout",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert logout.status_code == 204

    refresh = client.post(
        "/api/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert refresh.status_code == 401


@pytest.mark.asyncio
async def test_inactive_user_cannot_login(client: TestClient, db: AsyncSession):
    org = Organization(name="Inactive User Org", slug="inactive-user-org", plan="standard")
    db.add(org)
    await db.commit()
    await db.refresh(org)

    user = User(
        email="inactive-user@example.com",
        hashed_password=hash_password("password123"),
        full_name="Inactive User",
        role="admin",
        org_id=org.id,
        is_active=False,
    )
    db.add(user)
    await db.commit()

    response = client.post(
        "/api/auth/login",
        json={"email": "inactive-user@example.com", "password": "password123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Inactive user"


@pytest.mark.asyncio
async def test_inactive_organization_cannot_login(client: TestClient, db: AsyncSession):
    org = Organization(
        name="Inactive Org",
        slug="inactive-org-login",
        plan="standard",
        is_active=False,
    )
    db.add(org)
    await db.commit()
    await db.refresh(org)

    user = User(
        email="inactive-org-user@example.com",
        hashed_password=hash_password("password123"),
        full_name="Inactive Org User",
        role="admin",
        org_id=org.id,
        is_active=True,
    )
    db.add(user)
    await db.commit()

    response = client.post(
        "/api/auth/login",
        json={"email": "inactive-org-user@example.com", "password": "password123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Inactive organization"


@pytest.mark.asyncio
async def test_access_token_cannot_be_used_as_refresh_token(client: TestClient, db: AsyncSession):
    org = Organization(name="Token Type Org", slug="token-type-org", plan="standard")
    db.add(org)
    await db.commit()
    await db.refresh(org)

    user = User(
        email="token-type@example.com",
        hashed_password=hash_password("password123"),
        full_name="Token Type User",
        role="admin",
        org_id=org.id,
    )
    db.add(user)
    await db.commit()

    login = client.post(
        "/api/auth/login",
        json={"email": "token-type@example.com", "password": "password123"},
    )
    assert login.status_code == 200

    access_token = login.json()["access_token"]

    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": access_token},
    )

    assert response.status_code == 401

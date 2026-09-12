import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.auth.utils import hash_password


def test_user_registration(client: TestClient, db: AsyncSession):
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "securepass123",
        "full_name": "New User",
        "role": "viewer",
        "org_id": "test-org-id",
    })
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"


def test_login_success(client: TestClient, db: AsyncSession):
    org = Organization(name="Test", slug="test", plan="starter")
    db.add(org)
    db.commit()
    user = User(email="login@example.com", hashed_password=hash_password("password123"), full_name="Login User", role="admin", org_id=org.id, is_verified=True)
    db.add(user)
    db.commit()

    response = client.post("/api/v1/auth/login", json={"email": "login@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_failure(client: TestClient):
    response = client.post("/api/v1/auth/login", json={"email": "wrong@example.com", "password": "wrongpass"})
    assert response.status_code == 401

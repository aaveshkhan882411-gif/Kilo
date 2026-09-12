import pytest
from fastapi.testclient import TestClient


def test_protected_endpoint_without_token(client: TestClient):
    response = client.get("/api/v1/leads")
    assert response.status_code == 401


def test_protected_endpoint_with_invalid_token(client: TestClient):
    response = client.get("/api/v1/leads", headers={"Authorization": "Bearer invalid-token"})
    assert response.status_code == 401

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "GrowthAI" in response.json()["product"]

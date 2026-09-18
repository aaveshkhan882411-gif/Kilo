from fastapi.testclient import TestClient


def test_protected_endpoint_without_token(client: TestClient):
    response = client.get("/api/leads/")
    assert response.status_code == 403


def test_protected_endpoint_with_invalid_token(client: TestClient):
    response = client.get(
        "/api/leads/",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401

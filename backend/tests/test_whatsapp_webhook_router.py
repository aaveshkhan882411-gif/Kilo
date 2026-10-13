import hashlib
import hmac
import json

from app.config import settings
from app.integrations.whatsapp import WhatsAppIntegration


def _signature(body: bytes, secret: str) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    return f"sha256={digest}"


def test_whatsapp_webhook_verify_returns_exact_challenge(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "WHATSAPP_VERIFY_TOKEN",
        "test-verify-token",
    )

    response = client.get(
        "/api/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "test-verify-token",
            "hub.challenge": "123456789",
        },
    )

    assert response.status_code == 200
    assert response.text == "123456789"
    assert response.headers["content-type"].startswith("text/plain")


def test_whatsapp_webhook_verify_invalid_token(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "WHATSAPP_VERIFY_TOKEN",
        "correct-token",
    )

    response = client.get(
        "/api/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "123456789",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Verification failed"


def test_whatsapp_webhook_rejects_missing_signature(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "WHATSAPP_APP_SECRET",
        "test-app-secret",
    )

    body = json.dumps(
        {
            "object": "whatsapp_business_account",
        }
    ).encode("utf-8")

    response = client.post(
        "/api/whatsapp/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid WhatsApp webhook signature"


def test_whatsapp_webhook_rejects_invalid_signature(
    client,
    monkeypatch,
):
    monkeypatch.setattr(
        settings,
        "WHATSAPP_APP_SECRET",
        "test-app-secret",
    )

    body = json.dumps(
        {
            "object": "whatsapp_business_account",
        }
    ).encode("utf-8")

    response = client.post(
        "/api/whatsapp/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": "sha256=invalid",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid WhatsApp webhook signature"


def test_whatsapp_webhook_accepts_valid_signature(
    client,
    monkeypatch,
):
    secret = "test-app-secret"

    monkeypatch.setattr(
        settings,
        "WHATSAPP_APP_SECRET",
        secret,
    )

    async def fake_handle_inbound(self, payload):
        assert payload["object"] == "whatsapp_business_account"
        return type(
            "Result",
            (),
            {
                "success": True,
                "data": {"handled": True},
                "error": None,
            },
        )()

    monkeypatch.setattr(
        WhatsAppIntegration,
        "handle_inbound",
        fake_handle_inbound,
    )

    body = json.dumps(
        {
            "object": "whatsapp_business_account",
        }
    ).encode("utf-8")

    response = client.post(
        "/api/whatsapp/webhook",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Hub-Signature-256": _signature(body, secret),
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "received"
    assert response.json()["handled"] is True

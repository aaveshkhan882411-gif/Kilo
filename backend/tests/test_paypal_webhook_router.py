import pytest
from sqlalchemy import select

from app.models import PayPalWebhookEvent
from app.integrations.paypal import PayPalIntegration


@pytest.mark.asyncio
async def test_paypal_webhook_idempotency(client, db, monkeypatch):
    async def fake_verify(self, headers, body):
        return True

    async def fake_handle(self, event):
        from app.integrations.paypal import IntegrationResult

        return IntegrationResult(
            success=True,
            data={
                "event_type": event["event_type"],
                "event_id": event["id"],
            },
        )

    monkeypatch.setattr(
        PayPalIntegration,
        "is_configured",
        lambda self: True,
    )
    monkeypatch.setattr(
        PayPalIntegration,
        "verify_webhook_signature",
        fake_verify,
    )
    monkeypatch.setattr(
        PayPalIntegration,
        "handle_webhook_event",
        fake_handle,
    )

    payload = {
        "id": "WH-IDEMPOTENCY-001",
        "event_type": "PAYMENT.CAPTURE.COMPLETED",
        "resource": {
            "id": "CAPTURE-TEST-001",
        },
    }

    first = client.post(
        "/api/paypal/webhook",
        json=payload,
    )

    assert first.status_code == 200
    assert first.json()["status"] == "received"
    assert first.json()["event_id"] == "WH-IDEMPOTENCY-001"

    second = client.post(
        "/api/paypal/webhook",
        json=payload,
    )

    assert second.status_code == 200
    assert second.json()["status"] == "already_processed"
    assert second.json()["event_id"] == "WH-IDEMPOTENCY-001"

    result = await db.execute(
        select(PayPalWebhookEvent).where(
            PayPalWebhookEvent.event_id == "WH-IDEMPOTENCY-001"
        )
    )

    events = result.scalars().all()

    assert len(events) == 1
    assert events[0].status == "processed"
    assert events[0].event_type == "PAYMENT.CAPTURE.COMPLETED"


def test_paypal_webhook_invalid_signature(client, monkeypatch):
    async def fake_verify(self, headers, body):
        return False

    monkeypatch.setattr(
        PayPalIntegration,
        "is_configured",
        lambda self: True,
    )
    monkeypatch.setattr(
        PayPalIntegration,
        "verify_webhook_signature",
        fake_verify,
    )

    response = client.post(
        "/api/paypal/webhook",
        json={
            "id": "WH-INVALID-001",
            "event_type": "PAYMENT.CAPTURE.COMPLETED",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid PayPal webhook signature"

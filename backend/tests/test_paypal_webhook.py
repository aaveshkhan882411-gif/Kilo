import pytest

from app.integrations.paypal import PayPalIntegration


@pytest.mark.asyncio
async def test_paypal_webhook_verification_disabled():
    integration = PayPalIntegration()
    result = await integration.verify_webhook_signature({}, b"")
    assert result is False


@pytest.mark.asyncio
async def test_paypal_webhook_event_handling():
    integration = PayPalIntegration()
    result = await integration.handle_webhook_event(
        {
            "id": "WH-TEST-001",
            "event_type": "payment.completed",
        }
    )

    assert result.success is True
    assert result.data["event_type"] == "payment.completed"
    assert result.data["event_id"] == "WH-TEST-001"


@pytest.mark.asyncio
async def test_paypal_webhook_invalid_event():
    integration = PayPalIntegration()
    result = await integration.handle_webhook_event({})

    assert result.success is False
    assert result.error == "INVALID_WEBHOOK_EVENT"

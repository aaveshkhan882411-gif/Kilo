import pytest
from app.integrations.paypal import PayPalIntegration
from app.config import settings


def test_paypal_webhook_verification_disabled():
    integration = PayPalIntegration()
    assert integration.verify_webhook_signature({}, b"") is True


@pytest.mark.asyncio
async def test_paypal_webhook_event_handling():
    integration = PayPalIntegration()
    result = await integration.handle_webhook_event({"event_type": "payment.completed"})
    assert result.success is True
    assert result.data["event"]["event_type"] == "payment.completed"

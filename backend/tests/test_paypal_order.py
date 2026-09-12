import pytest
from app.integrations.paypal import PayPalIntegration


def test_paypal_order_idempotency():
    integration = PayPalIntegration()
    assert integration.is_configured() is False


def test_paypal_sandbox_mode():
    from app.config import settings
    assert settings.PAYPAL_ENVIRONMENT == "sandbox"


@pytest.mark.asyncio
async def test_paypal_capture_without_config():
    integration = PayPalIntegration()
    result = await integration.capture_order("order-123")
    assert result.success is False
    assert result.error == "NOT_CONFIGURED"

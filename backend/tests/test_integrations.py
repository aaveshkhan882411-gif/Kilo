import pytest
from app.integrations.paypal import PayPalIntegration
from app.integrations.whatsapp import WhatsAppIntegration
from app.integrations.email import EmailIntegration
from app.integrations.voice import VoiceIntegration
from app.config import settings


def test_paypal_not_configured():
    integration = PayPalIntegration()
    assert integration.is_configured() is False


def test_whatsapp_not_configured():
    integration = WhatsAppIntegration()
    assert integration.is_configured() is False


def test_email_not_configured():
    integration = EmailIntegration()
    assert integration.is_configured() is False


def test_voice_not_configured():
    integration = VoiceIntegration()
    assert integration.is_configured() is False


@pytest.mark.asyncio
async def test_paypal_returns_not_configured():
    integration = PayPalIntegration()
    result = await integration.create_order(100.0)
    assert result.success is False
    assert result.error == "NOT_CONFIGURED"


@pytest.mark.asyncio
async def test_whatsapp_returns_not_configured():
    integration = WhatsAppIntegration()
    result = await integration.send_message("+1234567890", "Hello")
    assert result.success is False
    assert result.error == "NOT_CONFIGURED"

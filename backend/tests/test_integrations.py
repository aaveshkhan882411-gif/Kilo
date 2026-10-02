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


@pytest.mark.asyncio
async def test_whatsapp_send_message_success(monkeypatch):
    integration = WhatsAppIntegration()

    monkeypatch.setattr(settings, "WHATSAPP_ACCESS_TOKEN", "test-token")
    monkeypatch.setattr(settings, "WHATSAPP_PHONE_NUMBER_ID", "123456789")
    monkeypatch.setattr(
        settings,
        "WHATSAPP_API_VERSION",
        "v23.0",
        raising=False,
    )

    class FakeResponse:
        status_code = 200
        is_success = True

        def json(self):
            return {
                "messaging_product": "whatsapp",
                "messages": [{"id": "wamid.test-message"}],
            }

    class FakeClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, headers, json):
            assert url == (
                "https://graph.facebook.com/"
                "v23.0/123456789/messages"
            )
            assert headers["Authorization"] == "Bearer test-token"
            assert json == {
                "messaging_product": "whatsapp",
                "to": "+1234567890",
                "type": "text",
                "text": {"body": "Hello"},
            }
            return FakeResponse()

    monkeypatch.setattr(
        "app.integrations.whatsapp.httpx.AsyncClient",
        FakeClient,
    )

    result = await integration.send_message(
        "+1234567890",
        "Hello",
    )

    assert result.success is True
    assert result.data == {
        "message_id": "wamid.test-message",
    }

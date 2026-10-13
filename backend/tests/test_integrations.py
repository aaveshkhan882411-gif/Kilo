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

def test_whatsapp_webhook_signature_verification(monkeypatch):
    import hashlib
    import hmac

    integration = WhatsAppIntegration()

    secret = "test-app-secret"
    body = b'{"object":"whatsapp_business_account"}'

    monkeypatch.setattr(
        settings,
        "WHATSAPP_APP_SECRET",
        secret,
    )

    digest = hmac.new(
        secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    assert integration.verify_webhook_signature(
        body,
        f"sha256={digest}",
    ) is True

    assert integration.verify_webhook_signature(
        body,
        "sha256=invalid",
    ) is False

    assert integration.verify_webhook_signature(
        body,
        None,
    ) is False

    assert integration.verify_webhook_signature(
        body,
        digest,
    ) is False


def test_whatsapp_webhook_signature_requires_app_secret(monkeypatch):
    integration = WhatsAppIntegration()

    monkeypatch.setattr(
        settings,
        "WHATSAPP_APP_SECRET",
        "",
    )

    assert integration.verify_webhook_signature(
        b'{"object":"whatsapp_business_account"}',
        "sha256=anything",
    ) is False


def _whatsapp_inbound_payload(phone_number_id, message_id):
    return {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "field": "messages",
                "value": {
                    "metadata": {
                        "phone_number_id": phone_number_id,
                    },
                    "messages": [{
                        "from": "919876543210",
                        "id": message_id,
                        "type": "text",
                        "text": {"body": "Hello GrowthAI"},
                    }],
                },
            }],
        }],
    }


@pytest.mark.asyncio
async def test_whatsapp_inbound_persists_message_for_active_tenant(
    test_org, monkeypatch
):
    import app.integrations.whatsapp as whatsapp_module
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from conftest import TestingSessionFactory
    from app.models import Integration, WhatsAppWebhookEvent
    from sqlalchemy import select

    monkeypatch.setattr(
        whatsapp_module, "async_session_factory", TestingSessionFactory
    )

    async with TestingSessionFactory() as session:
        session.add(Integration(
            org_id=test_org.id,
            provider="whatsapp",
            config={"phone_number_id": "phone-tenant-1"},
            status="active",
        ))
        await session.commit()

    result = await WhatsAppIntegration().handle_inbound(
        _whatsapp_inbound_payload("phone-tenant-1", "wamid-persist-test")
    )

    assert result.success is True
    assert result.data["received"] == 1

    async with TestingSessionFactory() as session:
        query = await session.execute(
            select(WhatsAppWebhookEvent).where(
                WhatsAppWebhookEvent.message_id == "wamid-persist-test"
            )
        )
        event = query.scalar_one()
        assert event.org_id == test_org.id
        assert event.sender_phone == "919876543210"
        assert event.message_body == "Hello GrowthAI"


@pytest.mark.asyncio
async def test_whatsapp_inbound_duplicate_is_not_saved_twice(
    test_org, monkeypatch
):
    import app.integrations.whatsapp as whatsapp_module
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from conftest import TestingSessionFactory
    from app.models import Integration, WhatsAppWebhookEvent
    from sqlalchemy import select, func

    monkeypatch.setattr(
        whatsapp_module, "async_session_factory", TestingSessionFactory
    )

    async with TestingSessionFactory() as session:
        session.add(Integration(
            org_id=test_org.id,
            provider="whatsapp",
            config={"phone_number_id": "phone-tenant-2"},
            status="active",
        ))
        await session.commit()

    payload = _whatsapp_inbound_payload(
        "phone-tenant-2", "wamid-duplicate-test"
    )
    integration = WhatsAppIntegration()

    first = await integration.handle_inbound(payload)
    second = await integration.handle_inbound(payload)

    assert first.success is True
    assert first.data["received"] == 1
    assert second.success is True
    assert second.data["duplicates"] == 1

    async with TestingSessionFactory() as session:
        query = await session.execute(
            select(func.count()).select_from(WhatsAppWebhookEvent).where(
                WhatsAppWebhookEvent.message_id == "wamid-duplicate-test"
            )
        )
        assert query.scalar_one() == 1


@pytest.mark.asyncio
async def test_whatsapp_inbound_unknown_phone_number_is_skipped(
    test_org, monkeypatch
):
    import app.integrations.whatsapp as whatsapp_module
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from conftest import TestingSessionFactory
    from app.models import Integration, WhatsAppWebhookEvent
    from sqlalchemy import select

    monkeypatch.setattr(
        whatsapp_module, "async_session_factory", TestingSessionFactory
    )

    async with TestingSessionFactory() as session:
        session.add(Integration(
            org_id=test_org.id,
            provider="whatsapp",
            config={"phone_number_id": "known-phone"},
            status="active",
        ))
        await session.commit()

    result = await WhatsAppIntegration().handle_inbound(
        _whatsapp_inbound_payload("unknown-phone", "wamid-unknown-test")
    )

    assert result.success is True
    assert result.data["received"] == 0
    assert result.data["skipped"] == 1

    async with TestingSessionFactory() as session:
        query = await session.execute(
            select(WhatsAppWebhookEvent).where(
                WhatsAppWebhookEvent.message_id == "wamid-unknown-test"
            )
        )
        assert query.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_whatsapp_inbound_database_failure_returns_failure(monkeypatch):
    import app.integrations.whatsapp as whatsapp_module

    def broken_session_factory():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(
        whatsapp_module, "async_session_factory", broken_session_factory
    )

    result = await WhatsAppIntegration().handle_inbound(
        _whatsapp_inbound_payload("phone-tenant-3", "wamid-db-error-test")
    )

    assert result.success is False
    assert result.error == "INBOUND_PROCESSING_FAILED"

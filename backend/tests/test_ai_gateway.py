import pytest

from app.ai.providers import MockProvider, VLLMProvider
from app.ai.gateway import AIGateway
from app.config import settings


@pytest.mark.asyncio
async def test_mock_provider_returns_response():
    provider = MockProvider()
    health = await provider.health_check()

    assert health["status"] == "healthy"
    assert health["provider"] == "mock"


def test_gateway_uses_configured_provider(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "mock")

    gateway = AIGateway()

    assert isinstance(gateway.provider, MockProvider)


@pytest.mark.asyncio
async def test_vllm_provider_not_configured():
    provider = VLLMProvider()
    health = await provider.health_check()

    assert health["status"] == "not_configured"
    assert health["provider"] == "vllm"

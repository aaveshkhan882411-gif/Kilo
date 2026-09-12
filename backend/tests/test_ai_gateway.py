import pytest
from app.ai.providers import MockProvider, VLLMProvider
from app.ai.gateway import AIGateway
from app.config import settings


def test_mock_provider_returns_response():
    provider = MockProvider()
    assert provider.health_check()["status"] == "healthy"


def test_gateway_uses_mock_provider():
    assert settings.AI_PROVIDER == "mock"


def test_vllm_provider_not_configured():
    provider = VLLMProvider()
    assert provider.health_check()["status"] == "not_configured"

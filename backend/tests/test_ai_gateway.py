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
async def test_vllm_provider_health_check_unavailable_without_server():
    provider = VLLMProvider(
        base_url="http://127.0.0.1:65530/v1",
    )

    health = await provider.health_check()

    assert health["provider"] == "vllm"
    assert health["status"] == "unavailable"


@pytest.mark.asyncio
async def test_vllm_provider_generate_parses_chat_completion(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "model": "growthai-model",
                "choices": [
                    {
                        "message": {
                            "content": "Hello from GrowthAI",
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": {
                    "total_tokens": 42,
                },
            }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            self.kwargs = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, url, headers, json):
            assert url == "http://vllm.test/v1/chat/completions"
            assert headers["Content-Type"] == "application/json"
            assert headers["Authorization"] == "Bearer test-key"
            assert json["model"] == "growthai-model"
            assert json["messages"][0]["content"] == "Test prompt"
            assert json["max_tokens"] == 128
            assert json["temperature"] == 0.2
            assert json["stream"] is False

            return FakeResponse()

    monkeypatch.setattr(
        "app.ai.providers.base.httpx.AsyncClient",
        FakeAsyncClient,
    )

    provider = VLLMProvider(
        base_url="http://vllm.test/v1/",
        api_key="test-key",
    )

    result = await provider.generate(
        prompt="Test prompt",
        model="growthai-model",
        max_tokens=128,
        temperature=0.2,
    )

    assert result["text"] == "Hello from GrowthAI"
    assert result["model"] == "growthai-model"
    assert result["tokens_used"] == 42
    assert result["finish_reason"] == "stop"


@pytest.mark.asyncio
async def test_vllm_provider_generate_handles_connection_error(monkeypatch):
    import httpx

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, url, headers, json):
            raise httpx.ConnectError("connection failed")

    monkeypatch.setattr(
        "app.ai.providers.base.httpx.AsyncClient",
        FakeAsyncClient,
    )

    provider = VLLMProvider(
        base_url="http://vllm.test/v1",
    )

    result = await provider.generate(
        prompt="Test prompt",
        model="growthai-model",
        max_tokens=128,
        temperature=0.2,
    )

    assert result["error"] == "vllm_connection_error"
    assert result["provider"] == "vllm"


@pytest.mark.asyncio
async def test_vllm_provider_generate_handles_empty_response(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "model": "growthai-model",
                "choices": [],
            }

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def post(self, url, headers, json):
            return FakeResponse()

    monkeypatch.setattr(
        "app.ai.providers.base.httpx.AsyncClient",
        FakeAsyncClient,
    )

    provider = VLLMProvider(
        base_url="http://vllm.test/v1",
    )

    result = await provider.generate(
        prompt="Test prompt",
        model="growthai-model",
        max_tokens=128,
        temperature=0.2,
    )

    assert result["error"] == "vllm_empty_response"
    assert result["provider"] == "vllm"


@pytest.mark.asyncio
async def test_vllm_provider_health_check(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

        async def get(self, url, headers):
            assert url == "http://vllm.test/v1/models"
            return FakeResponse()

    monkeypatch.setattr(
        "app.ai.providers.base.httpx.AsyncClient",
        FakeAsyncClient,
    )

    provider = VLLMProvider(
        base_url="http://vllm.test/v1",
    )

    result = await provider.health_check()

    assert result["status"] == "healthy"
    assert result["provider"] == "vllm"


def test_gateway_requires_vllm_model(monkeypatch):
    from app.ai.gateway import AIGateway

    monkeypatch.setattr(settings, "AI_PROVIDER", "vllm")
    monkeypatch.setattr(settings, "VLLM_MODEL", "")

    gateway = AIGateway()

    with pytest.raises(
        ValueError,
        match="VLLM_MODEL must be configured",
    ):
        gateway._resolve_model(None)


def test_gateway_uses_configured_vllm_model(monkeypatch):
    from app.ai.gateway import AIGateway

    monkeypatch.setattr(settings, "AI_PROVIDER", "vllm")
    monkeypatch.setattr(settings, "VLLM_MODEL", "growthai-model")

    gateway = AIGateway()

    assert gateway._resolve_model(None) == "growthai-model"
    assert gateway._resolve_model("explicit-model") == "explicit-model"


def test_gateway_keeps_mock_default_for_mock_provider(monkeypatch):
    from app.ai.gateway import AIGateway

    monkeypatch.setattr(settings, "AI_PROVIDER", "mock")

    gateway = AIGateway()

    assert gateway._resolve_model(None) == "mock"
    assert gateway._resolve_model("custom-model") == "custom-model"

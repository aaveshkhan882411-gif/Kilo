from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncIterator
from app.config import settings


class BaseProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, model: str, max_tokens: int, temperature: float, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def stream(self, prompt: str, model: str, max_tokens: int, temperature: float, context: Optional[Dict[str, Any]] = None) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        pass


class MockProvider(BaseProvider):
    async def generate(self, prompt: str, model: str, max_tokens: int, temperature: float, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "text": f"[MOCK] Response to: {prompt[:100]}",
            "model": model or "mock",
            "tokens_used": len(prompt.split()),
            "finish_reason": "stop",
        }

    async def stream(self, prompt: str, model: str, max_tokens: int, temperature: float, context: Optional[Dict[str, Any]] = None) -> AsyncIterator[str]:
        response = f"[MOCK] Response to: {prompt[:100]}"
        for chunk in response.split():
            yield chunk + " "

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "provider": "mock"}


class VLLMProvider(BaseProvider):
    def __init__(self, base_url: str = settings.VLLM_BASE_URL, api_key: str = settings.VLLM_API_KEY):
        self.base_url = base_url
        self.api_key = api_key

    async def generate(self, prompt: str, model: str, max_tokens: int, temperature: float, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"error": "VLLM provider not implemented"}

    async def stream(self, prompt: str, model: str, max_tokens: int, temperature: float, context: Optional[Dict[str, Any]] = None) -> AsyncIterator[str]:
        yield ""

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "not_configured", "provider": "vllm"}

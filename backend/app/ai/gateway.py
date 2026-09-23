from typing import Dict, Any, Optional, AsyncIterator
from app.ai.providers import BaseProvider, MockProvider, VLLMProvider
from app.config import settings


class AIGateway:
    def __init__(self):
        self.provider = self._select_provider()

    def _select_provider(self) -> BaseProvider:
        if settings.AI_PROVIDER == "vllm":
            return VLLMProvider()
        return MockProvider()

    def _resolve_model(self, model: Optional[str]) -> str:
        if model:
            return model

        if settings.AI_PROVIDER == "vllm":
            if not settings.VLLM_MODEL:
                raise ValueError(
                    "VLLM_MODEL must be configured when AI_PROVIDER=vllm"
                )
            return settings.VLLM_MODEL

        return "mock"

    async def generate(self, prompt: str, model: Optional[str] = None, max_tokens: int = 1024, temperature: float = 0.7, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resolved_model = self._resolve_model(model)
        return await self.provider.generate(
            prompt,
            resolved_model,
            max_tokens,
            temperature,
            context,
        )

    async def stream(self, prompt: str, model: Optional[str] = None, max_tokens: int = 1024, temperature: float = 0.7, context: Optional[Dict[str, Any]] = None) -> AsyncIterator[str]:
        resolved_model = self._resolve_model(model)
        async for chunk in self.provider.stream(
            prompt,
            resolved_model,
            max_tokens,
            temperature,
            context,
        ):
            yield chunk

    async def health_check(self) -> Dict[str, Any]:
        return await self.provider.health_check()


ai_gateway = AIGateway()

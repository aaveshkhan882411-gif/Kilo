from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, AsyncIterator

import httpx

from app.config import settings


class BaseProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        pass


class MockProvider(BaseProvider):
    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {
            "text": f"[MOCK] Response to: {prompt[:100]}",
            "model": model or "mock",
            "tokens_used": len(prompt.split()),
            "finish_reason": "stop",
        }

    async def stream(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        response = f"[MOCK] Response to: {prompt[:100]}"
        for chunk in response.split():
            yield chunk + " "

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "healthy", "provider": "mock"}


class VLLMProvider(BaseProvider):
    def __init__(
        self,
        base_url: str = settings.VLLM_BASE_URL,
        api_key: str = settings.VLLM_API_KEY,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    async def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

        except httpx.HTTPStatusError as exc:
            return {
                "error": "vllm_http_error",
                "status_code": exc.response.status_code,
                "provider": "vllm",
            }
        except httpx.RequestError:
            return {
                "error": "vllm_connection_error",
                "provider": "vllm",
            }
        except ValueError:
            return {
                "error": "vllm_invalid_response",
                "provider": "vllm",
            }

        choices = data.get("choices") or []

        if not choices:
            return {
                "error": "vllm_empty_response",
                "provider": "vllm",
            }

        message = choices[0].get("message") or {}
        usage = data.get("usage") or {}

        return {
            "text": message.get("content", ""),
            "model": data.get("model", model),
            "tokens_used": usage.get("total_tokens"),
            "finish_reason": choices[0].get("finish_reason"),
        }

    async def stream(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> AsyncIterator[str]:
        yield ""

    async def health_check(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self._headers(),
                )
                response.raise_for_status()

            return {
                "status": "healthy",
                "provider": "vllm",
            }

        except httpx.HTTPStatusError as exc:
            return {
                "status": "unhealthy",
                "provider": "vllm",
                "status_code": exc.response.status_code,
            }
        except httpx.RequestError:
            return {
                "status": "unavailable",
                "provider": "vllm",
            }

from typing import Dict, Any, Optional

import httpx

from app.integrations.base import BaseIntegration, IntegrationResult
from app.config import settings


class WhatsAppIntegration(BaseIntegration):
    provider = "whatsapp"

    def is_configured(self) -> bool:
        return bool(
            settings.WHATSAPP_ACCESS_TOKEN
            and settings.WHATSAPP_PHONE_NUMBER_ID
        )

    def _messages_url(self) -> str:
        version = getattr(settings, "WHATSAPP_API_VERSION", "").strip()

        if version:
            version = version.rstrip("/")
            return (
                f"https://graph.facebook.com/"
                f"{version}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
            )

        return (
            f"https://graph.facebook.com/"
            f"{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
        )

    async def send_message(
        self,
        to: str,
        message: str,
    ) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(
                success=False,
                error="NOT_CONFIGURED",
            )

        to = to.strip()
        message = message.strip()

        if not to or not message:
            return IntegrationResult(
                success=False,
                error="INVALID_PARAMETERS",
            )

        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {
                "body": message,
            },
        }

        headers = {
            "Authorization": (
                f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}"
            ),
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    self._messages_url(),
                    headers=headers,
                    json=payload,
                )

            if response.is_success:
                provider_data = response.json()

                messages = provider_data.get("messages") or []
                message_id = (
                    messages[0].get("id")
                    if messages and isinstance(messages[0], dict)
                    else None
                )

                return IntegrationResult(
                    success=True,
                    data={
                        "message_id": message_id,
                    },
                )

            try:
                error_data = response.json()
            except ValueError:
                error_data = {}

            provider_error = error_data.get("error", {})
            error_message = (
                provider_error.get("message")
                if isinstance(provider_error, dict)
                else None
            )

            return IntegrationResult(
                success=False,
                error=error_message or "WHATSAPP_API_ERROR",
                data={
                    "status_code": response.status_code,
                },
            )

        except httpx.RequestError:
            return IntegrationResult(
                success=False,
                error="REQUEST_FAILED",
            )
        except Exception:
            return IntegrationResult(
                success=False,
                error="UNEXPECTED_ERROR",
            )

    async def verify_webhook(
        self,
        mode: str,
        token: str,
        challenge: Optional[str],
    ) -> Optional[str]:
        if (
            mode == "subscribe"
            and token == settings.WHATSAPP_VERIFY_TOKEN
        ):
            return challenge

        return None

    async def handle_inbound(
        self,
        payload: Dict[str, Any],
    ) -> IntegrationResult:
        return IntegrationResult(
            success=True,
            data={"message": "inbound handled"},
        )

    async def connect(self) -> IntegrationResult:
        configured = self.is_configured()

        return IntegrationResult(
            success=configured,
            error=None if configured else "NOT_CONFIGURED",
        )

    async def health_check(self) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(
                success=False,
                error="NOT_CONFIGURED",
            )

        return IntegrationResult(success=True)

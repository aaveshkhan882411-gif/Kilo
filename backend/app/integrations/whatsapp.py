from typing import Dict, Any, Optional
import httpx
import hmac
import hashlib
from app.integrations.base import BaseIntegration, IntegrationResult
from app.config import settings


class WhatsAppIntegration(BaseIntegration):
    provider = "whatsapp"

    def is_configured(self) -> bool:
        return bool(settings.WHATSAPP_ACCESS_TOKEN and settings.WHATSAPP_PHONE_NUMBER_ID)

    async def send_message(self, to: str, message: str) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(success=False, error="NOT_CONFIGURED")
        return IntegrationResult(success=False, error="Not implemented")

    async def verify_webhook(self, mode: str, token: str, challenge: Optional[str]) -> Optional[str]:
        if token == settings.WHATSAPP_VERIFY_TOKEN:
            return challenge
        return None

    async def handle_inbound(self, payload: Dict[str, Any]) -> IntegrationResult:
        return IntegrationResult(success=True, data={"message": "inbound handled"})

    async def connect(self) -> IntegrationResult:
        return IntegrationResult(success=self.is_configured(), error=None if self.is_configured() else "NOT_CONFIGURED")

    async def health_check(self) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(success=False, error="NOT_CONFIGURED")
        return IntegrationResult(success=True)

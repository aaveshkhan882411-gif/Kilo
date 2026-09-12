from typing import Dict, Any, Optional
import httpx
from app.integrations.base import BaseIntegration, IntegrationResult
from app.config import settings


class GoogleOAuthIntegration(BaseIntegration):
    provider = "google_oauth"

    def is_configured(self) -> bool:
        return bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)

    def get_authorization_url(self) -> str:
        if not self.is_configured():
            return ""
        return f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}&response_type=code&scope=openid%20email%20profile"

    async def exchange_code(self, code: str) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(success=False, error="NOT_CONFIGURED")
        return IntegrationResult(success=False, error="Not implemented")

    async def get_user_info(self, access_token: str) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(success=False, error="NOT_CONFIGURED")
        return IntegrationResult(success=False, error="Not implemented")

    async def connect(self) -> IntegrationResult:
        return IntegrationResult(success=self.is_configured(), error=None if self.is_configured() else "NOT_CONFIGURED")

    async def health_check(self) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(success=False, error="NOT_CONFIGURED")
        return IntegrationResult(success=True)

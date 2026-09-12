from app.integrations.base import BaseIntegration, IntegrationResult
from app.config import settings


class VoiceIntegration(BaseIntegration):
    provider = "voice"

    def is_configured(self) -> bool:
        return bool(settings.VOICE_API_KEY or settings.VOICE_ACCOUNT_SID)

    async def transcribe(self, audio: bytes) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(success=False, error="NOT_CONFIGURED")
        return IntegrationResult(success=False, error="Not implemented")

    async def synthesize(self, text: str) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(success=False, error="NOT_CONFIGURED")
        return IntegrationResult(success=False, error="Not implemented")

    async def connect(self) -> IntegrationResult:
        return IntegrationResult(success=self.is_configured(), error=None if self.is_configured() else "NOT_CONFIGURED")

    async def health_check(self) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(success=False, error="NOT_CONFIGURED")
        return IntegrationResult(success=True)

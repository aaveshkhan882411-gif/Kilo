from typing import Dict, Any, Optional
from app.integrations.base import BaseIntegration, IntegrationResult
from app.config import settings


class CalendarIntegration(BaseIntegration):
    provider = "google_calendar"

    def is_configured(self) -> bool:
        return False

    async def create_event(self, event: Dict[str, Any]) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(success=False, error="NOT_CONFIGURED")
        return IntegrationResult(success=False, error="Not implemented")

    async def connect(self) -> IntegrationResult:
        return IntegrationResult(success=self.is_configured(), error=None if self.is_configured() else "NOT_CONFIGURED")

    async def health_check(self) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(success=False, error="NOT_CONFIGURED")
        return IntegrationResult(success=True)

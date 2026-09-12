from typing import Dict, Any, Optional
from app.integrations.base import BaseIntegration, IntegrationResult
from app.integrations.paypal import PayPalIntegration
from app.integrations.google import GoogleOAuthIntegration
from app.integrations.whatsapp import WhatsAppIntegration
from app.integrations.email import EmailIntegration
from app.integrations.voice import VoiceIntegration
from app.integrations.calendar import CalendarIntegration


class IntegrationGateway:
    def __init__(self):
        self._integrations: Dict[str, BaseIntegration] = {
            "paypal": PayPalIntegration(),
            "google_oauth": GoogleOAuthIntegration(),
            "whatsapp": WhatsAppIntegration(),
            "email": EmailIntegration(),
            "voice": VoiceIntegration(),
            "google_calendar": CalendarIntegration(),
        }

    def get(self, provider: str) -> Optional[BaseIntegration]:
        return self._integrations.get(provider)

    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        results = {}
        for name, integration in self._integrations.items():
            results[name] = await integration.health_check()
        return results


gateway = IntegrationGateway()

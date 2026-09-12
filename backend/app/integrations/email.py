from typing import Dict, Any, Optional
import aiosmtplib
from email.message import EmailMessage
from app.integrations.base import BaseIntegration, IntegrationResult
from app.config import settings


class EmailIntegration(BaseIntegration):
    provider = "email"

    def is_configured(self) -> bool:
        return bool(settings.SMTP_USER and settings.SMTP_PASSWORD)

    async def send_email(self, to: str, subject: str, body: str, html: Optional[str] = None) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(success=False, error="NOT_CONFIGURED")
        message = EmailMessage()
        message["From"] = settings.SMTP_FROM
        message["To"] = to
        message["Subject"] = subject
        message.set_content(body)
        if html:
            message.add_alternative(html, subtype="html")
        try:
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                start_tls=True,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
            )
            return IntegrationResult(success=True)
        except Exception as exc:
            return IntegrationResult(success=False, error=str(exc))

    async def connect(self) -> IntegrationResult:
        return IntegrationResult(success=self.is_configured(), error=None if self.is_configured() else "NOT_CONFIGURED")

    async def health_check(self) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(success=False, error="NOT_CONFIGURED")
        return IntegrationResult(success=True)

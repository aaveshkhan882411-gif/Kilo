from typing import Dict, Any, List, Optional
import aiosmtplib
from email.message import EmailMessage
from app.config import settings


class NotificationService:
    @staticmethod
    async def send_email(to: str, subject: str, body: str, html: Optional[str] = None) -> Dict[str, Any]:
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            return {"success": False, "error": "NOT_CONFIGURED"}
        message = EmailMessage()
        message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.SMTP_FROM}>"
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
            return {"success": True}
        except Exception as exc:
            return {"success": False, "error": str(exc)}

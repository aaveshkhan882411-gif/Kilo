from typing import Dict, Any, Optional

import hashlib
import hmac

import httpx
from app.models import Integration, WhatsAppWebhookEvent
from app.database import async_session_factory
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

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

    def verify_webhook_signature(
        self,
        raw_body: bytes,
        signature_header: Optional[str],
    ) -> bool:
        if not settings.WHATSAPP_APP_SECRET:
            return False

        if not signature_header:
            return False

        prefix = "sha256="
        if not signature_header.startswith(prefix):
            return False

        provided_signature = signature_header[len(prefix):].strip()

        if not provided_signature:
            return False

        expected_signature = hmac.new(
            settings.WHATSAPP_APP_SECRET.encode("utf-8"),
            raw_body,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(
            expected_signature,
            provided_signature,
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
        if not isinstance(payload, dict):
            return IntegrationResult(
                success=False,
                error="INVALID_WEBHOOK_PAYLOAD",
            )

        entries = payload.get("entry", [])
        if not isinstance(entries, list):
            return IntegrationResult(
                success=False,
                error="INVALID_WEBHOOK_PAYLOAD",
            )

        received = 0
        duplicates = 0
        skipped = 0

        try:
            for entry in entries:
                if not isinstance(entry, dict):
                    skipped += 1
                    continue

                changes = entry.get("changes", [])
                if not isinstance(changes, list):
                    skipped += 1
                    continue

                for change in changes:
                    if not isinstance(change, dict):
                        skipped += 1
                        continue

                    value = change.get("value", {})
                    if not isinstance(value, dict):
                        skipped += 1
                        continue

                    metadata = value.get("metadata", {})
                    if not isinstance(metadata, dict):
                        metadata = {}

                    phone_number_id = str(
                        metadata.get("phone_number_id", "")
                    ).strip()

                    messages = value.get("messages", [])
                    if not isinstance(messages, list):
                        skipped += 1
                        continue

                    # Status notifications without messages need no
                    # message-event record.
                    if not messages:
                        continue

                    for message in messages:
                        if not isinstance(message, dict):
                            skipped += 1
                            continue

                        message_id = str(message.get("id", "")).strip()
                        sender_phone = str(
                            message.get("from", "")
                        ).strip()
                        message_type = str(
                            message.get("type", "unknown")
                        ).strip() or "unknown"

                        if not phone_number_id or not message_id or not sender_phone:
                            skipped += 1
                            continue

                        text_data = message.get("text", {})
                        message_body = (
                            text_data.get("body")
                            if message_type == "text"
                            and isinstance(text_data, dict)
                            else None
                        )

                        async with async_session_factory() as session:
                            # Resolve the tenant only through an active
                            # integration with an exact phone-number match.
                            result = await session.execute(
                                select(Integration).where(
                                    Integration.provider == "whatsapp",
                                    Integration.status == "active",
                                )
                            )
                            integrations = result.scalars().all()

                            matches = [
                                item for item in integrations
                                if isinstance(item.config, dict)
                                and str(
                                    item.config.get("phone_number_id", "")
                                ).strip() == phone_number_id
                            ]

                            # Never guess a tenant when no unique mapping
                            # exists.
                            if len(matches) != 1:
                                skipped += 1
                                continue

                            existing = await session.execute(
                                select(WhatsAppWebhookEvent.id).where(
                                    WhatsAppWebhookEvent.message_id
                                    == message_id
                                )
                            )
                            if existing.scalar_one_or_none() is not None:
                                duplicates += 1
                                continue

                            event = WhatsAppWebhookEvent(
                                message_id=message_id,
                                org_id=matches[0].org_id,
                                phone_number_id=phone_number_id,
                                sender_phone=sender_phone,
                                message_type=message_type,
                                message_body=message_body,
                                status="received",
                                payload=__import__("json").dumps(
                                    message,
                                    ensure_ascii=False,
                                    separators=(",", ":"),
                                ),
                            )
                            session.add(event)

                            try:
                                await session.commit()
                                received += 1
                            except IntegrityError:
                                await session.rollback()

                                # A concurrent webhook may have inserted
                                # this message after our initial lookup.
                                duplicate_check = await session.execute(
                                    select(WhatsAppWebhookEvent.id).where(
                                        WhatsAppWebhookEvent.message_id
                                        == message_id
                                    )
                                )
                                if duplicate_check.scalar_one_or_none() is not None:
                                    duplicates += 1
                                else:
                                    raise

            return IntegrationResult(
                success=True,
                data={
                    "message": "inbound processed",
                    "received": received,
                    "duplicates": duplicates,
                    "skipped": skipped,
                },
            )

        except Exception:
            return IntegrationResult(
                success=False,
                error="INBOUND_PROCESSING_FAILED",
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

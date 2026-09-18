from typing import Any, Dict

import httpx

from app.config import settings
from app.integrations.base import BaseIntegration, IntegrationResult


class PayPalIntegration(BaseIntegration):
    provider = "paypal"

    def is_configured(self) -> bool:
        return bool(
            settings.PAYPAL_CLIENT_ID
            and settings.PAYPAL_CLIENT_SECRET
            and settings.PAYPAL_BASE_URL
        )

    async def get_access_token(self) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(
                success=False,
                error="NOT_CONFIGURED",
            )

        url = f"{settings.PAYPAL_BASE_URL.rstrip('/')}/v1/oauth2/token"

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    url,
                    data={"grant_type": "client_credentials"},
                    auth=(
                        settings.PAYPAL_CLIENT_ID,
                        settings.PAYPAL_CLIENT_SECRET,
                    ),
                    headers={
                        "Accept": "application/json",
                        "Accept-Language": "en_US",
                    },
                )

            if response.status_code != 200:
                return IntegrationResult(
                    success=False,
                    error=f"PAYPAL_AUTH_FAILED:{response.status_code}",
                )

            data = response.json()
            access_token = data.get("access_token")

            if not access_token:
                return IntegrationResult(
                    success=False,
                    error="PAYPAL_AUTH_TOKEN_MISSING",
                )

            return IntegrationResult(
                success=True,
                data={
                    "access_token": access_token,
                    "token_type": data.get("token_type", "Bearer"),
                    "expires_in": data.get("expires_in"),
                },
            )

        except httpx.HTTPError as exc:
            return IntegrationResult(
                success=False,
                error=f"PAYPAL_HTTP_ERROR:{type(exc).__name__}",
            )

    async def create_order(
        self,
        amount: float,
        currency: str = "USD",
    ) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(
                success=False,
                error="NOT_CONFIGURED",
            )

        token_result = await self.get_access_token()

        if not token_result.success:
            return token_result

        access_token = token_result.data["access_token"]
        url = f"{settings.PAYPAL_BASE_URL.rstrip('/')}/v2/checkout/orders"

        payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": currency,
                        "value": f"{amount:.2f}",
                    }
                }
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )

            if response.status_code not in (200, 201):
                return IntegrationResult(
                    success=False,
                    error=f"PAYPAL_ORDER_CREATE_FAILED:{response.status_code}",
                )

            data = response.json()

            return IntegrationResult(
                success=True,
                data={
                    "order_id": data.get("id"),
                    "status": data.get("status"),
                    "links": [
                        {
                            "href": link.get("href", ""),
                            "rel": link.get("rel", ""),
                            "method": link.get("method", ""),
                        }
                        for link in data.get("links", [])
                    ],
                },
            )

        except httpx.HTTPError as exc:
            return IntegrationResult(
                success=False,
                error=f"PAYPAL_HTTP_ERROR:{type(exc).__name__}",
            )

    async def capture_order(self, order_id: str) -> IntegrationResult:
        if not self.is_configured():
            return IntegrationResult(
                success=False,
                error="NOT_CONFIGURED",
            )

        if not order_id.strip():
            return IntegrationResult(
                success=False,
                error="INVALID_ORDER_ID",
            )

        token_result = await self.get_access_token()

        if not token_result.success:
            return token_result

        access_token = token_result.data["access_token"]
        url = (
            f"{settings.PAYPAL_BASE_URL.rstrip('/')}"
            f"/v2/checkout/orders/{order_id}/capture"
        )

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )

            if response.status_code not in (200, 201):
                return IntegrationResult(
                    success=False,
                    error=f"PAYPAL_CAPTURE_FAILED:{response.status_code}",
                )

            data = response.json()

            capture = None

            for unit in data.get("purchase_units", []):
                payments = unit.get("payments", {})
                captures = payments.get("captures", [])
                if captures:
                    capture = captures[0]
                    break

            if not capture:
                return IntegrationResult(
                    success=False,
                    error="PAYPAL_CAPTURE_DATA_MISSING",
                )

            amount_data = capture.get("amount", {})

            return IntegrationResult(
                success=True,
                data={
                    "capture_id": capture.get("id"),
                    "status": capture.get("status"),
                    "amount": float(amount_data.get("value", 0)),
                    "currency": amount_data.get("currency_code", ""),
                    "order_id": data.get("id", order_id),
                },
            )

        except httpx.HTTPError as exc:
            return IntegrationResult(
                success=False,
                error=f"PAYPAL_HTTP_ERROR:{type(exc).__name__}",
            )

    async def verify_webhook_signature(
        self,
        headers: Dict[str, str],
        body: bytes,
    ) -> bool:
        if not self.is_configured() or not settings.PAYPAL_WEBHOOK_ID:
            return False

        try:
            event = __import__("json").loads(body.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            return False

        required_headers = {
            "transmission_id": headers.get("paypal-transmission-id"),
            "transmission_time": headers.get("paypal-transmission-time"),
            "cert_url": headers.get("paypal-cert-url"),
            "auth_algo": headers.get("paypal-auth-algo"),
            "transmission_sig": headers.get("paypal-transmission-sig"),
        }

        if not all(required_headers.values()):
            return False

        token_result = await self.get_access_token()

        if not token_result.success:
            return False

        access_token = token_result.data["access_token"]

        url = (
            f"{settings.PAYPAL_BASE_URL.rstrip('/')}"
            "/v1/notifications/verify-webhook-signature"
        )

        payload: Dict[str, Any] = {
            **required_headers,
            "webhook_id": settings.PAYPAL_WEBHOOK_ID,
            "webhook_event": event,
        }

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                    },
                )

            if response.status_code != 200:
                return False

            return response.json().get("verification_status") == "SUCCESS"

        except httpx.HTTPError:
            return False

    async def handle_webhook_event(
        self,
        event: Dict[str, Any],
    ) -> IntegrationResult:
        event_type = event.get("event_type")

        if not event_type:
            return IntegrationResult(
                success=False,
                error="INVALID_WEBHOOK_EVENT",
            )

        return IntegrationResult(
            success=True,
            data={
                "event_type": event_type,
                "event_id": event.get("id"),
            },
        )

    async def connect(self) -> IntegrationResult:
        return await self.get_access_token()

    async def health_check(self) -> IntegrationResult:
        result = await self.get_access_token()

        if not result.success:
            return result

        return IntegrationResult(
            success=True,
            data={"provider": self.provider},
        )

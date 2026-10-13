import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse

from app.integrations.whatsapp import WhatsAppIntegration

router = APIRouter()


@router.get("/webhook")
async def webhook_verify(request: Request):
    integration = WhatsAppIntegration()

    mode = request.query_params.get("hub.mode", "")
    token = request.query_params.get("hub.verify_token", "")
    challenge = request.query_params.get("hub.challenge")

    verified_challenge = await integration.verify_webhook(
        mode=mode,
        token=token,
        challenge=challenge,
    )

    if verified_challenge is None:
        raise HTTPException(
            status_code=403,
            detail="Verification failed",
        )

    return PlainTextResponse(verified_challenge)


@router.post("/webhook")
async def webhook_inbound(request: Request):
    integration = WhatsAppIntegration()

    raw_body = await request.body()

    signature = request.headers.get("X-Hub-Signature-256")

    if not integration.verify_webhook_signature(
        raw_body=raw_body,
        signature_header=signature,
    ):
        raise HTTPException(
            status_code=403,
            detail="Invalid WhatsApp webhook signature",
        )

    try:
        payload = json.loads(raw_body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid WhatsApp webhook payload",
        )

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=400,
            detail="Invalid WhatsApp webhook payload",
        )

    result = await integration.handle_inbound(payload)

    if not result.success:
        raise HTTPException(
            status_code=503,
            detail="Webhook processing failed; retry later",
        )

    data = result.data or {}

    return {
        "status": "received",
        **data,
    }

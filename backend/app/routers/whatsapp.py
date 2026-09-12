from fastapi import APIRouter, Depends, Request, HTTPException, status
from app.config import settings
from app.integrations.whatsapp import WhatsAppIntegration

router = APIRouter()


@router.get("/webhook")
async def webhook_verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(challenge) if challenge else "OK"
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/webhook")
async def webhook_inbound(request: Request):
    if not settings.WHATSAPP_ACCESS_TOKEN:
        return {"status": "ignored", "reason": "not_configured"}
    body = await request.json()
    return {"status": "received"}

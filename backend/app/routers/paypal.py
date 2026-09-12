from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.config import settings
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.payment import PayPalOrderResponse, PayPalCaptureResponse
from app.integrations.paypal import PayPalIntegration

router = APIRouter()


@router.post("/orders", response_model=PayPalOrderResponse)
async def create_order(
    amount: float,
    current_user: User = Depends(get_current_active_user),
):
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="PayPal not configured")

    paypal = PayPalIntegration()
    result = await paypal.create_order(amount, currency="USD")
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return PayPalOrderResponse(**result.data)


@router.post("/orders/{order_id}/capture", response_model=PayPalCaptureResponse)
async def capture_order(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
):
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="PayPal not configured")

    paypal = PayPalIntegration()
    result = await paypal.capture_order(order_id)
    if not result.success:
        raise HTTPException(status_code=500, detail=result.error)
    return PayPalCaptureResponse(**result.data)


@router.post("/webhook")
async def paypal_webhook(request: Request):
    if not settings.PAYPAL_WEBHOOK_ID:
        return {"status": "ignored", "reason": "webhook verification disabled"}
    body = await request.body()
    paypal = PayPalIntegration()
    verified = await paypal.verify_webhook_signature(dict(request.headers), body)
    if not verified:
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    return {"status": "received"}

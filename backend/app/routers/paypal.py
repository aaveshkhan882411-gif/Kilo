from calendar import monthrange
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.integrations.paypal import PayPalIntegration
from app.models import Payment, Subscription, PayPalWebhookEvent
from app.models.user import User
from app.schemas.payment import PayPalCaptureResponse, PayPalOrderResponse
from app.services.pricing import get_plan, get_price

router = APIRouter()


def _validate_plan_price(plan: str, billing_cycle: str) -> tuple[dict, Decimal]:
    if billing_cycle not in {"monthly", "annual"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="billing_cycle must be monthly or annual",
        )

    plan_data = get_plan(plan)

    if not plan_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan",
        )

    price = get_price(plan, billing_cycle)

    if price is None or price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unavailable plan price",
        )

    return plan_data, Decimal(str(price)).quantize(Decimal("0.01"))


def _add_period(start: datetime, billing_cycle: str) -> datetime:
    if billing_cycle == "annual":
        try:
            return start.replace(year=start.year + 1)
        except ValueError:
            return start.replace(
                year=start.year + 1,
                month=2,
                day=28,
            )

    month = start.month
    year = start.year + (1 if month == 12 else 0)
    next_month = 1 if month == 12 else month + 1
    last_day = monthrange(year, next_month)[1]

    return start.replace(
        year=year,
        month=next_month,
        day=min(start.day, last_day),
    )


async def _activate_subscription(
    db: AsyncSession,
    payment: Payment,
    activated_at: datetime | None = None,
) -> Subscription:
    now = activated_at or datetime.utcnow()

    result = await db.execute(
        select(Subscription)
        .where(Subscription.org_id == payment.org_id)
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    subscription = result.scalar_one_or_none()

    if subscription is None:
        subscription = Subscription(
            org_id=payment.org_id,
            plan=payment.plan,
            status="active",
            current_period_start=now,
            current_period_end=_add_period(now, payment.billing_cycle),
        )
        db.add(subscription)
        await db.flush()
    else:
        subscription.plan = payment.plan
        subscription.status = "active"
        subscription.current_period_start = now
        subscription.current_period_end = _add_period(
            now,
            payment.billing_cycle,
        )
        await db.flush()

    payment.subscription_id = subscription.id
    await db.flush()

    return subscription


@router.post("/orders", response_model=PayPalOrderResponse)
async def create_order(
    plan: str,
    billing_cycle: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    _, expected_amount = _validate_plan_price(plan, billing_cycle)

    paypal = PayPalIntegration()

    if not paypal.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PayPal not configured",
        )

    result = await paypal.create_order(
        amount=float(expected_amount),
        currency="USD",
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=result.error or "PayPal order creation failed",
        )

    order_id = result.data.get("order_id")

    if not order_id:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="PayPal did not return an order ID",
        )

    payment = Payment(
        org_id=current_user.org_id,
        amount=expected_amount,
        currency="USD",
        status="pending",
        plan=plan,
        billing_cycle=billing_cycle,
        paypal_order_id=order_id,
    )

    db.add(payment)
    await db.commit()

    return PayPalOrderResponse(**result.data)


@router.post(
    "/orders/{order_id}/capture",
    response_model=PayPalCaptureResponse,
)
async def capture_order(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Payment).where(
            Payment.paypal_order_id == order_id,
            Payment.org_id == current_user.org_id,
        )
    )
    payment = result.scalar_one_or_none()

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment order not found",
        )

    if payment.status == "completed" and payment.paypal_capture_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment already captured",
        )

    paypal = PayPalIntegration()

    if not paypal.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PayPal not configured",
        )

    result = await paypal.capture_order(order_id)

    if not result.success:
        payment.status = "failed"
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=result.error or "PayPal capture failed",
        )

    captured_amount = Decimal(
        str(result.data["amount"])
    ).quantize(Decimal("0.01"))
    captured_currency = result.data["currency"]

    if captured_currency != payment.currency:
        payment.status = "failed"
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Captured currency does not match payment currency",
        )

    expected_amount = Decimal(
        str(payment.amount)
    ).quantize(Decimal("0.01"))

    if captured_amount != expected_amount:
        payment.status = "failed"
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Captured amount does not match expected payment amount",
        )

    capture_id = result.data.get("capture_id")

    if not capture_id:
        payment.status = "failed"
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="PayPal capture ID missing",
        )

    payment.paypal_capture_id = capture_id
    payment.status = "completed"

    await _activate_subscription(db, payment)

    await db.commit()

    return PayPalCaptureResponse(
        capture_id=capture_id,
        status=result.data["status"],
        amount=float(captured_amount),
        currency=captured_currency,
    )


@router.post("/webhook")
async def paypal_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    body = await request.body()

    paypal = PayPalIntegration()

    if not paypal.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PayPal not configured",
        )

    verified = await paypal.verify_webhook_signature(
        dict(request.headers),
        body,
    )

    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid PayPal webhook signature",
        )

    try:
        event: dict[str, Any] = await request.json()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook JSON",
        ) from exc

    event_id = event.get("id")
    event_type = event.get("event_type")

    if not isinstance(event_id, str) or not event_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing PayPal event ID",
        )

    if not isinstance(event_type, str) or not event_type.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing PayPal event type",
        )

    existing_result = await db.execute(
        select(PayPalWebhookEvent).where(
            PayPalWebhookEvent.event_id == event_id
        )
    )
    existing_event = existing_result.scalar_one_or_none()

    if existing_event is not None:
        if existing_event.status == "processed":
            return {
                "status": "already_processed",
                "event_id": event_id,
                "event_type": event_type,
            }

        if existing_event.status == "processing":
            return {
                "status": "already_processing",
                "event_id": event_id,
                "event_type": event_type,
            }

        existing_event.status = "processing"
        existing_event.error = None
        webhook_event = existing_event
    else:
        webhook_event = PayPalWebhookEvent(
            event_id=event_id,
            event_type=event_type,
            status="processing",
            payload=body.decode("utf-8"),
        )
        db.add(webhook_event)

    try:
        await db.commit()

        result = await paypal.handle_webhook_event(event)

        if not result.success:
            webhook_event.status = "failed"
            webhook_event.error = (
                result.error or "WEBHOOK_PROCESSING_FAILED"
            )
            await db.commit()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Webhook processing failed",
            )

        webhook_event.status = "processed"
        webhook_event.processed_at = datetime.utcnow()

        await db.commit()

        return {
            "status": "received",
            "event_id": event_id,
            "event_type": event_type,
        }

    except HTTPException:
        raise
    except Exception as exc:
        await db.rollback()

        try:
            webhook_event.status = "failed"
            webhook_event.error = type(exc).__name__
            await db.commit()
        except Exception:
            await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook processing failed",
        ) from exc

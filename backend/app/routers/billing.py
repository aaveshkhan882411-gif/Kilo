from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models.user import User
from app.models import Payment, Subscription
from app.schemas.payment import PaymentResponse
from app.schemas.subscription import PlanInfo, SubscriptionResponse
from app.services.pricing import PRICING


router = APIRouter()


PLANS = [
    PlanInfo(
        id=plan["id"],
        name=plan["name"],
        price_monthly=plan["price_monthly"],
        price_annual=plan["price_annual"],
        agent_limit=plan["agent_limit"],
        features=plan["features"],
        trial_days=7 if plan["id"] == "standard" else 5,
    )
    for plan in PRICING.values()
]


@router.get("/plans", response_model=list[PlanInfo])
async def list_plans():
    return PLANS


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Subscription)
        .where(Subscription.org_id == current_user.org_id)
        .order_by(Subscription.created_at.desc())
        .limit(1)
    )
    subscription = result.scalar_one_or_none()

    if subscription is None:
        raise HTTPException(status_code=404, detail="No active subscription")

    return subscription


@router.post("/subscription", response_model=SubscriptionResponse, status_code=201)
async def create_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    raise HTTPException(
        status_code=400,
        detail="Subscription is activated after verified payment capture",
    )


@router.get("/payments", response_model=list[PaymentResponse])
async def list_payments(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Payment)
        .where(Payment.org_id == current_user.org_id)
        .order_by(Payment.created_at.desc())
    )
    return list(result.scalars().all())

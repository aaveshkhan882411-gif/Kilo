from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_active_user
from app.schemas.subscription import PlanInfo, SubscriptionResponse

router = APIRouter()


PLANS = [
    PlanInfo(
        id="standard",
        name="Standard",
        price_monthly=1999.0,
        agent_limit=4,
        features=["4 AI Agents", "CRM", "Email", "Basic Support"],
        trial_days=14,
    ),
    PlanInfo(
        id="premium",
        name="Premium",
        price_monthly=2999.0,
        price_annual=35000.0,
        agent_limit=7,
        features=["7 AI Agents", "CRM", "Email", "WhatsApp", "Priority Support"],
        trial_days=14,
    ),
    PlanInfo(
        id="enterprise",
        name="Enterprise",
        price_monthly=3999.0,
        price_annual=45000.0,
        agent_limit=13,
        features=["13 AI Agents", "Full Workforce", "Dedicated Support", "Custom Integrations"],
        trial_days=14,
    ),
    PlanInfo(
        id="autonomous",
        name="Autonomous",
        price_monthly=0.0,
        agent_limit=20,
        features=["All 20 Agents", "Full Autonomy", "White Label", "Dedicated Infrastructure"],
        trial_days=30,
    ),
]


@router.get("/plans", response_model=list[PlanInfo])
async def list_plans():
    return PLANS


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(current_user: User = Depends(get_current_active_user)):
    return SubscriptionResponse(id="", org_id=current_user.org_id, plan="starter", status="inactive", created_at=datetime.utcnow(), updated_at=datetime.utcnow())


@router.post("/subscription", response_model=SubscriptionResponse, status_code=201)
async def create_subscription(current_user: User = Depends(get_current_active_user)):
    return SubscriptionResponse(id="", org_id=current_user.org_id, plan="starter", status="inactive", created_at=datetime.utcnow(), updated_at=datetime.utcnow())


@router.get("/payments", response_model=list[dict])
async def list_payments(current_user: User = Depends(get_current_active_user)):
    return []

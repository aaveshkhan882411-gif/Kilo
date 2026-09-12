from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class SubscriptionCreate(BaseModel):
    plan: str = Field(..., max_length=50)
    paypal_subscription_id: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: str
    org_id: str
    plan: str
    status: str
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    paypal_subscription_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PlanInfo(BaseModel):
    id: str
    name: str
    price_monthly: float
    price_annual: Optional[float] = None
    agent_limit: int
    features: list[str]
    trial_days: int = 14

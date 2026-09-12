from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AnalyticsResponse(BaseModel):
    id: str
    org_id: str
    metric: str
    value: float
    period_start: datetime
    period_end: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_leads: int
    total_customers: int
    total_deals: int
    total_revenue: float
    conversion_rate: float
    active_workflows: int
    pending_tasks: int
    upcoming_appointments: int

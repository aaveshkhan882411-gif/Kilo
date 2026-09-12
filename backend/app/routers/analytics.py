from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_active_user
from app.schemas.analytics import DashboardStats

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
async def dashboard(current_user: User = Depends(get_current_active_user)):
    return DashboardStats(
        total_leads=0,
        total_customers=0,
        total_deals=0,
        total_revenue=0.0,
        conversion_rate=0.0,
        active_workflows=0,
        pending_tasks=0,
        upcoming_appointments=0,
    )


@router.get("/metrics/{metric}")
async def get_metric(metric: str, current_user: User = Depends(get_current_active_user)):
    return {"metric": metric, "value": 0.0}

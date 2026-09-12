from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from app.config import settings


class BillingService:
    PLANS = {
        "standard": {"agent_limit": 4, "price_monthly": 1999.0},
        "premium": {"agent_limit": 7, "price_monthly": 2999.0},
        "enterprise": {"agent_limit": 13, "price_monthly": 3999.0},
        "autonomous": {"agent_limit": 20, "price_monthly": 0.0},
    }

    @classmethod
    def get_plan(cls, plan_id: str) -> Optional[Dict[str, Any]]:
        return cls.PLANS.get(plan_id)

    @classmethod
    def can_deploy_agent(cls, plan_id: str, current_count: int) -> bool:
        plan = cls.PLANS.get(plan_id)
        if not plan:
            return False
        return current_count < plan["agent_limit"]

    @classmethod
    def list_plans(cls) -> List[Dict[str, Any]]:
        return [{"id": k, **v} for k, v in cls.PLANS.items()]

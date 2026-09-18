from typing import Any, Dict, List, Optional

from app.services.pricing import PRICING, get_plan, get_price


class BillingService:
    PLANS = PRICING

    @classmethod
    def get_plan(cls, plan_id: str) -> Optional[Dict[str, Any]]:
        return get_plan(plan_id)

    @classmethod
    def get_price(cls, plan_id: str, billing_cycle: str) -> Optional[float]:
        return get_price(plan_id, billing_cycle)

    @classmethod
    def can_deploy_agent(cls, plan_id: str, current_count: int) -> bool:
        plan = cls.get_plan(plan_id)
        if not plan:
            return False
        return current_count < plan["agent_limit"]

    @classmethod
    def list_plans(cls) -> List[Dict[str, Any]]:
        return list(PRICING.values())

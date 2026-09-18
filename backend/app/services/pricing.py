from typing import Final


PRICING: Final[dict[str, dict]] = {
    "standard": {
        "id": "standard",
        "name": "Standard",
        "price_monthly": 1999.0,
        "price_annual": 25000.0,
        "agent_limit": 4,
        "features": [
            "4 AI Agents",
            "CRM",
            "Email",
            "Basic Support",
        ],
    },
    "premium": {
        "id": "premium",
        "name": "Premium",
        "price_monthly": 2999.0,
        "price_annual": 35000.0,
        "agent_limit": 7,
        "features": [
            "7 AI Agents",
            "CRM",
            "Email",
            "WhatsApp",
            "Priority Support",
        ],
    },
    "enterprise": {
        "id": "enterprise",
        "name": "Enterprise",
        "price_monthly": 3999.0,
        "price_annual": 45000.0,
        "agent_limit": 13,
        "features": [
            "13 AI Agents",
            "Full Workforce",
            "Dedicated Support",
            "Custom Integrations",
        ],
    },
    "autonomous": {
        "id": "autonomous",
        "name": "Autonomous",
        "price_monthly": 5999.0,
        "price_annual": 59999.0,
        "agent_limit": 20,
        "features": [
            "All 20 Agents",
            "Full Autonomy",
            "White Label",
            "Dedicated Infrastructure",
        ],
    },
}


def get_plan(plan_id: str) -> dict | None:
    return PRICING.get(plan_id)


def get_price(plan_id: str, billing_cycle: str) -> float | None:
    plan = get_plan(plan_id)
    if not plan:
        return None

    if billing_cycle == "monthly":
        return plan["price_monthly"]

    if billing_cycle == "annual":
        return plan["price_annual"]

    return None

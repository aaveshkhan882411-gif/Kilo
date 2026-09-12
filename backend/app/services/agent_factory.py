from typing import Dict, Any, List, Optional


class AgentFactory:
    @staticmethod
    def analyze_business(website_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "industry": "technology",
            "products": website_data.get("products", []),
            "services": website_data.get("services", []),
            "opportunities": ["Website optimization", "Lead automation", "CRM integration"],
            "risks": ["Low conversion rate", "High bounce rate"],
            "bottlenecks": ["Manual lead qualification", "Slow follow-up"],
        }

    @staticmethod
    def recommend_workforce(business_analysis: Dict[str, Any], plan: str) -> Dict[str, Any]:
        from app.services.billing_service import BillingService
        plan_info = BillingService.get_plan(plan)
        agent_limit = plan_info["agent_limit"] if plan_info else 4
        recommended = [
            "ai-lead-intelligence",
            "ai-growth-strategist",
            "ai-sales",
            "ai-followup",
            "ai-appointment",
            "ai-email",
            "ai-crm",
        ][:agent_limit]
        return {
            "recommended_agents": recommended,
            "reasoning": f"Recommended {len(recommended)} agents for {plan} plan based on business analysis",
            "estimated_roi": 3.5,
            "implementation_priority": recommended,
            "required_plan": plan,
        }

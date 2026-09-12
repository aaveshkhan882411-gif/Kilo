from typing import Dict, Any, List, Optional


class BusinessBrain:
    INDUSTRY_PROFILES = {
        "technology": {
            "typical_products": ["SaaS", "API", "Platform"],
            "typical_services": ["Consulting", "Support", "Implementation"],
            "typical_channels": ["Online", "Referral", "Partnerships"],
        },
        "retail": {
            "typical_products": ["Goods", "Merchandise"],
            "typical_services": ["Delivery", "Installation", "Support"],
            "typical_channels": ["Online", "In-store", "Social"],
        },
        "services": {
            "typical_products": [],
            "typical_services": ["Consulting", "Advisory", "Implementation"],
            "typical_channels": ["Referral", "Networking", "Content"],
        },
    }

    @classmethod
    def analyze(cls, industry: str, description: str) -> Dict[str, Any]:
        profile = cls.INDUSTRY_PROFILES.get(industry.lower(), cls.INDUSTRY_PROFILES["services"])
        return {
            "industry": industry,
            "products": profile["typical_products"],
            "services": profile["typical_services"],
            "lead_channels": profile["typical_channels"],
            "opportunities": ["Increase digital presence", "Automate lead follow-up", "Improve conversion rate"],
            "risks": ["Market saturation", "Competitor pricing"],
            "bottlenecks": ["Manual lead processing", "Slow response time"],
        }

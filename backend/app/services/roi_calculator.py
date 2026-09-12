from typing import Dict, Any


class ROICalculator:
    @staticmethod
    def calculate(monthly_leads: float, current_conversion_rate: float, average_customer_value: float, missed_leads_percentage: float, current_response_time_hours: float, workforce_cost_monthly: float) -> Dict[str, Any]:
        converted = monthly_leads * (current_conversion_rate / 100.0)
        missed = monthly_leads * (missed_leads_percentage / 100.0)
        recovered = missed * (current_conversion_rate / 100.0) * 1.5
        monthly_revenue_opportunity = recovered * average_customer_value
        annual_revenue_opportunity = monthly_revenue_opportunity * 12
        workforce_cost_annual = workforce_cost_monthly * 12
        net_annual_opportunity = annual_revenue_opportunity - workforce_cost_annual
        roi_multiple = (net_annual_opportunity / workforce_cost_annual) if workforce_cost_annual > 0 else 0.0
        return {
            "estimated_monthly_leads_recovered": round(recovered, 2),
            "estimated_conversion_improvement": round(missed_leads_percentage * 0.3, 2),
            "estimated_monthly_revenue_opportunity": round(monthly_revenue_opportunity, 2),
            "annual_revenue_opportunity": round(annual_revenue_opportunity, 2),
            "workforce_cost_annual": round(workforce_cost_annual, 2),
            "net_annual_opportunity": round(net_annual_opportunity, 2),
            "roi_multiple": round(roi_multiple, 2),
            "notes": "Estimated additional revenue opportunity based on provided inputs",
        }

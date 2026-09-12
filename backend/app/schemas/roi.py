from pydantic import BaseModel, Field
from typing import Optional


class ROICalculatorRequest(BaseModel):
    monthly_leads: int = Field(..., ge=0)
    current_conversion_rate: float = Field(..., ge=0, le=100)
    average_customer_value: float = Field(..., gt=0)
    missed_leads_percentage: float = Field(50.0, ge=0, le=100)
    current_response_time_hours: float = Field(24.0, ge=0)
    workforce_cost_monthly: float = Field(1999.0, ge=0)


class ROICalculatorResponse(BaseModel):
    estimated_monthly_leads_recovered: float
    estimated_conversion_improvement: float
    estimated_monthly_revenue_opportunity: float
    annual_revenue_opportunity: float
    workforce_cost_annual: float
    net_annual_opportunity: float
    roi_multiple: float
    notes: str

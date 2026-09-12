import pytest
from app.services.roi_calculator import ROICalculator


def test_roi_calculation():
    result = ROICalculator.calculate(
        monthly_leads=1000,
        current_conversion_rate=5.0,
        average_customer_value=500.0,
        missed_leads_percentage=50.0,
        current_response_time_hours=24.0,
        workforce_cost_monthly=1999.0,
    )
    assert "estimated_monthly_revenue_opportunity" in result
    assert "annual_revenue_opportunity" in result
    assert result["estimated_monthly_revenue_opportunity"] >= 0
    assert "Estimated additional revenue opportunity" in result["notes"]


def test_roi_does_not_present_as_guaranteed():
    result = ROICalculator.calculate(
        monthly_leads=500,
        current_conversion_rate=10.0,
        average_customer_value=1000.0,
        missed_leads_percentage=30.0,
        current_response_time_hours=12.0,
        workforce_cost_monthly=2999.0,
    )
    assert "guaranteed" not in result["notes"].lower()

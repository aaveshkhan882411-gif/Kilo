import pytest
from app.services.billing_service import BillingService


def test_standard_plan_allows_4_agents():
    assert BillingService.can_deploy_agent("standard", 3) is True
    assert BillingService.can_deploy_agent("standard", 4) is False


def test_premium_plan_allows_7_agents():
    assert BillingService.can_deploy_agent("premium", 6) is True
    assert BillingService.can_deploy_agent("premium", 7) is False


def test_enterprise_plan_allows_13_agents():
    assert BillingService.can_deploy_agent("enterprise", 12) is True
    assert BillingService.can_deploy_agent("enterprise", 13) is False


def test_unknown_plan_rejects():
    assert BillingService.can_deploy_agent("unknown", 0) is False

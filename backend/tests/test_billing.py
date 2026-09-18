import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models import Payment, Subscription
from app.database import get_db


client = TestClient(app)


def test_billing_plans():
    response = client.get("/api/billing/plans")
    assert response.status_code == 200

    plans = response.json()
    assert len(plans) == 4

    prices = {plan["id"]: plan["price_monthly"] for plan in plans}

    assert prices["standard"] == 1999.0
    assert prices["premium"] == 2999.0
    assert prices["enterprise"] == 3999.0
    assert prices["autonomous"] == 5999.0

    assert all(plan["trial_days"] in [5, 7] for plan in plans)


def test_subscription_creation_is_blocked_without_payment(auth_headers):
    response = client.post(
        "/api/billing/subscription",
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "verified payment capture" in response.json()["detail"]


@pytest.mark.asyncio
async def test_payment_and_subscription_are_tenant_scoped(test_org, test_user, db):
    from app.models.organization import Organization
    from app.models.user import User
    from app.auth.utils import hash_password

    org_b = Organization(
        name="Other Org",
        slug="other-org",
        plan="standard",
    )
    db.add(org_b)
    await db.commit()
    await db.refresh(org_b)

    payment_a = Payment(
        org_id=test_org.id,
        amount=1999,
        currency="USD",
        status="completed",
        plan="standard",
        billing_cycle="monthly",
    )

    payment_b = Payment(
        org_id=org_b.id,
        amount=2999,
        currency="USD",
        status="completed",
        plan="premium",
        billing_cycle="monthly",
    )

    subscription_a = Subscription(
        org_id=test_org.id,
        plan="standard",
        status="active",
    )

    subscription_b = Subscription(
        org_id=org_b.id,
        plan="premium",
        status="active",
    )

    db.add_all([
        payment_a,
        payment_b,
        subscription_a,
        subscription_b,
    ])
    await db.commit()

    payment_result = await db.execute(
        select(Payment).where(Payment.org_id == test_user.org_id)
    )
    payments = list(payment_result.scalars().all())

    subscription_result = await db.execute(
        select(Subscription).where(Subscription.org_id == test_user.org_id)
    )
    subscriptions = list(subscription_result.scalars().all())

    assert len(payments) == 1
    assert payments[0].plan == "standard"

    assert len(subscriptions) == 1
    assert subscriptions[0].plan == "standard"


def test_subscription_without_record_returns_404(auth_headers):
    response = client.get(
        "/api/billing/subscription",
        headers=auth_headers,
    )

    assert response.status_code == 404

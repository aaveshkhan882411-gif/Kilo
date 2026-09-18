import pytest
from sqlalchemy import select

from app.integrations.paypal import PayPalIntegration


def test_paypal_order_idempotency():
    integration = PayPalIntegration()
    assert integration.is_configured() is False


@pytest.mark.asyncio
async def test_paypal_capture_without_config():
    integration = PayPalIntegration()
    result = await integration.capture_order("order-123")
    assert result.success is False
    assert result.error == "NOT_CONFIGURED"


@pytest.mark.asyncio
async def test_paypal_create_order_without_config():
    integration = PayPalIntegration()
    result = await integration.create_order(1999.0, "USD")
    assert result.success is False
    assert result.error == "NOT_CONFIGURED"


@pytest.mark.asyncio
async def test_activate_subscription_from_completed_payment(test_org, db):
    from app.models import Payment, Subscription
    from app.routers.paypal import _activate_subscription

    payment = Payment(
        org_id=test_org.id,
        amount=1999,
        currency="USD",
        status="completed",
        plan="standard",
        billing_cycle="monthly",
        paypal_order_id="test-order-activation",
        paypal_capture_id="test-capture-activation",
    )

    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    await _activate_subscription(db, payment)

    await db.refresh(payment)

    result = await db.execute(
        select(Subscription).where(Subscription.org_id == test_org.id)
    )
    subscription = result.scalar_one()

    assert payment.subscription_id == subscription.id
    assert subscription.org_id == test_org.id
    assert subscription.plan == "standard"
    assert subscription.status == "active"
    assert subscription.current_period_start is not None
    assert subscription.current_period_end is not None


@pytest.mark.asyncio
async def test_activate_subscription_updates_existing_subscription(test_org, db):
    from app.models import Payment, Subscription
    from app.routers.paypal import _activate_subscription

    subscription = Subscription(
        org_id=test_org.id,
        plan="premium",
        status="active",
    )
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)

    payment = Payment(
        org_id=test_org.id,
        amount=1999,
        currency="USD",
        status="completed",
        plan="standard",
        billing_cycle="monthly",
        paypal_order_id="test-order-existing-sub",
        paypal_capture_id="test-capture-existing-sub",
    )

    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    await _activate_subscription(db, payment)

    await db.refresh(subscription)
    await db.refresh(payment)

    assert subscription.plan == "standard"
    assert subscription.status == "active"
    assert payment.subscription_id == subscription.id

import pytest

from app.services.workflow_execution_service import WorkflowExecutionService


@pytest.mark.asyncio
async def test_workflow_execution_requires_org_id():
    result = await WorkflowExecutionService.execute(
        workflow_id="workflow-1",
        context={},
    )

    assert result["success"] is False
    assert result["status"] == "invalid_execution_context"


@pytest.mark.asyncio
async def test_workflow_execution_requires_workflow_id():
    result = await WorkflowExecutionService.execute(
        workflow_id="",
        context={"org_id": "org-1"},
    )

    assert result["success"] is False
    assert result["status"] == "invalid_parameters"


@pytest.mark.asyncio
async def test_workflow_execution_loads_current_tenant_workflow(
    db,
    test_org,
    monkeypatch,
):
    from app.services import workflow_execution_service as service_module
    from app.models import Workflow
    from tests.conftest import TestingSessionFactory

    monkeypatch.setattr(
        service_module,
        "async_session_factory",
        TestingSessionFactory,
    )

    workflow = Workflow(
        org_id=test_org.id,
        name="Lead Follow Up",
        trigger_type="lead_created",
        actions=[{"type": "notify", "channel": "email"}],
        is_active=True,
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    result = await WorkflowExecutionService.execute(
        workflow_id=workflow.id,
        context={"org_id": test_org.id},
    )

    assert result["success"] is True
    assert result["status"] == "loaded"
    assert result["workflow"]["id"] == workflow.id
    assert result["workflow"]["org_id"] == test_org.id


@pytest.mark.asyncio
async def test_workflow_execution_cannot_cross_tenant(
    db,
    test_org,
):
    from app.models import Organization, Workflow

    other_org = Organization(
        name="Other Org",
        slug="other-org",
        plan="standard",
    )
    db.add(other_org)
    await db.commit()
    await db.refresh(other_org)

    workflow = Workflow(
        org_id=other_org.id,
        name="Secret Workflow",
        trigger_type="lead_created",
        actions=[{"type": "notify", "channel": "email"}],
        is_active=True,
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    result = await WorkflowExecutionService.execute(
        workflow_id=workflow.id,
        context={"org_id": test_org.id},
    )

    assert result["success"] is False
    assert result["status"] == "not_found"


@pytest.mark.asyncio
async def test_workflow_execution_skips_inactive_workflow(
    db,
    test_org,
    monkeypatch,
):
    from app.models import Workflow
    from app.services import workflow_execution_service as service_module
    from tests.conftest import TestingSessionFactory

    monkeypatch.setattr(
        service_module,
        "async_session_factory",
        TestingSessionFactory,
    )

    workflow = Workflow(
        org_id=test_org.id,
        name="Inactive Workflow",
        trigger_type="lead_created",
        actions=[{"type": "notify", "channel": "email"}],
        is_active=False,
    )
    db.add(workflow)
    await db.commit()
    await db.refresh(workflow)

    result = await WorkflowExecutionService.execute(
        workflow_id=workflow.id,
        context={"org_id": test_org.id},
    )

    assert result["success"] is False
    assert result["status"] == "workflow_inactive"


@pytest.mark.asyncio
async def test_workflow_execution_matches_trigger_type(
    db,
    test_org,
    monkeypatch,
):
    from app.models import Workflow
    from app.services import workflow_execution_service as service_module
    from tests.conftest import TestingSessionFactory

    monkeypatch.setattr(
        service_module,
        "async_session_factory",
        TestingSessionFactory,
    )

    matching = Workflow(
        org_id=test_org.id,
        name="Lead Created Workflow",
        trigger_type="lead_created",
        actions=[{"type": "notify", "channel": "email"}],
        is_active=True,
    )
    different = Workflow(
        org_id=test_org.id,
        name="Appointment Workflow",
        trigger_type="appointment_created",
        actions=[{"type": "notify", "channel": "email"}],
        is_active=True,
    )

    db.add_all([matching, different])
    await db.commit()

    result = await WorkflowExecutionService.find_matching_workflows(
        trigger_type="lead_created",
        context={"org_id": test_org.id},
    )

    assert result["success"] is True
    assert result["status"] == "matched"
    assert result["count"] == 1
    assert result["workflows"][0]["id"] == matching.id

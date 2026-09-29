from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_create_lead_enqueues_matching_workflow(
    client,
    auth_headers,
    test_user,
):
    matched = {
        "success": True,
        "status": "matched",
        "workflows": [
            {
                "id": "workflow-1",
                "org_id": test_user.org_id,
                "name": "New Lead Email",
                "trigger_type": "lead_created",
                "actions": [],
                "is_active": True,
            },
            {
                "id": "workflow-2",
                "org_id": test_user.org_id,
                "name": "New Lead Follow-up",
                "trigger_type": "lead_created",
                "actions": [],
                "is_active": True,
            },
        ],
        "count": 2,
    }

    queued = []

    async def fake_find_matching_workflows(trigger_type, context, db=None):
        assert trigger_type == "lead_created"
        assert context["org_id"] == test_user.org_id
        return matched

    def fake_delay(workflow_id, org_id):
        queued.append((workflow_id, org_id))

    with (
        patch(
            "app.routers.leads.WorkflowExecutionService.find_matching_workflows",
            new=fake_find_matching_workflows,
        ),
        patch(
            "app.routers.leads.process_workflow_task.delay",
            side_effect=fake_delay,
        ),
    ):
        response = client.post(
            "/api/leads/",
            headers=auth_headers,
            json={
                "first_name": "Workflow",
                "last_name": "Lead",
                "email": "workflow-lead@example.com",
                "phone": "9999999999",
                "company": "Workflow Test",
                "source": "test",
                "notes": "workflow trigger test",
            },
        )

    assert response.status_code == 201
    assert queued == [
        ("workflow-1", test_user.org_id),
        ("workflow-2", test_user.org_id),
    ]


@pytest.mark.asyncio
async def test_create_lead_survives_workflow_enqueue_failure(
    client,
    auth_headers,
    test_user,
):
    matched = {
        "success": True,
        "status": "matched",
        "workflows": [
            {
                "id": "workflow-failure",
                "org_id": test_user.org_id,
                "name": "Broker Failure Test",
                "trigger_type": "lead_created",
                "actions": [],
                "is_active": True,
            }
        ],
        "count": 1,
    }

    async def fake_find_matching_workflows(trigger_type, context, db=None):
        assert trigger_type == "lead_created"
        assert context["org_id"] == test_user.org_id
        return matched

    def failing_delay(workflow_id, org_id):
        raise RuntimeError("Celery broker unavailable")

    with (
        patch(
            "app.routers.leads.WorkflowExecutionService.find_matching_workflows",
            new=fake_find_matching_workflows,
        ),
        patch(
            "app.routers.leads.process_workflow_task.delay",
            side_effect=failing_delay,
        ),
    ):
        response = client.post(
            "/api/leads/",
            headers=auth_headers,
            json={
                "first_name": "Broker",
                "last_name": "Failure",
                "email": "broker-failure@example.com",
                "phone": "8888888888",
                "company": "Reliability Test",
                "source": "test",
                "notes": "workflow enqueue failure test",
            },
        )

    assert response.status_code == 201
    assert response.json()["email"] == "broker-failure@example.com"

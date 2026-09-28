from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_create_appointment_enqueues_matching_workflow(
    client,
    auth_headers,
    test_user,
):
    matched = {
        "success": True,
        "status": "matched",
        "workflows": [
            {
                "id": "workflow-appointment-1",
                "org_id": test_user.org_id,
                "name": "Appointment Follow-up",
                "trigger_type": "appointment_created",
                "actions": [],
                "is_active": True,
            },
            {
                "id": "workflow-appointment-2",
                "org_id": test_user.org_id,
                "name": "Appointment Notification",
                "trigger_type": "appointment_created",
                "actions": [],
                "is_active": True,
            },
        ],
        "count": 2,
    }

    queued = []

    async def fake_find_matching_workflows(trigger_type, context):
        assert trigger_type == "appointment_created"
        assert context["org_id"] == test_user.org_id
        return matched

    def fake_delay(workflow_id, org_id):
        queued.append((workflow_id, org_id))

    with (
        patch(
            "app.routers.appointments.WorkflowExecutionService.find_matching_workflows",
            new=fake_find_matching_workflows,
        ),
        patch(
            "app.routers.appointments.process_workflow_task.delay",
            side_effect=fake_delay,
        ),
    ):
        response = client.post(
            "/api/appointments/",
            headers=auth_headers,
            json={
                "title": "Workflow Appointment",
                "description": "Appointment workflow trigger test",
                "start_time": "2030-02-15T10:00:00",
                "end_time": "2030-02-15T11:00:00",
                "location": "Test Office",
                "organizer_id": test_user.id,
                "status": "scheduled",
            },
        )

    assert response.status_code == 201
    assert queued == [
        ("workflow-appointment-1", test_user.org_id),
        ("workflow-appointment-2", test_user.org_id),
    ]

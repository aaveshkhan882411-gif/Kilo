from unittest.mock import patch

from app.workers.tasks import process_workflow_task


def test_process_workflow_task_requires_workflow_id():
    result = process_workflow_task.run("", "org-1")

    assert result["success"] is False
    assert result["status"] == "invalid_parameters"
    assert result["workflow_id"] == ""


def test_process_workflow_task_requires_org_id():
    result = process_workflow_task.run("workflow-1", "")

    assert result["success"] is False
    assert result["status"] == "invalid_execution_context"
    assert result["workflow_id"] == "workflow-1"


def test_process_workflow_task_passes_trusted_org_context():
    expected = {
        "success": True,
        "status": "executed",
        "workflow_id": "workflow-1",
        "org_id": "org-1",
    }

    async def fake_execute(workflow_id, context):
        assert workflow_id == "workflow-1"
        assert context == {"org_id": "org-1"}
        return expected

    with patch(
        "app.services.workflow_execution_service.WorkflowExecutionService.execute",
        new=fake_execute,
    ):
        result = process_workflow_task.run(" workflow-1 ", " org-1 ")

    assert result == expected

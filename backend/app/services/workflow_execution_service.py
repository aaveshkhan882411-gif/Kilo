from typing import Any, Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.integrations.email import EmailIntegration
from app.models import Workflow


class WorkflowExecutionService:

    @staticmethod
    async def find_matching_workflows(
        trigger_type: str,
        context: Dict[str, Any] | None,
        db: AsyncSession | None = None,
    ) -> Dict[str, Any]:
        context = context or {}

        org_id = context.get("org_id")
        if not org_id:
            return {
                "success": False,
                "status": "invalid_execution_context",
                "workflows": [],
                "count": 0,
            }

        if not isinstance(trigger_type, str) or not trigger_type.strip():
            return {
                "success": False,
                "status": "invalid_parameters",
                "workflows": [],
                "count": 0,
            }

        async def _query(session: AsyncSession) -> Dict[str, Any]:
            result = await session.execute(
                select(Workflow)
                .where(
                    Workflow.org_id == org_id,
                    Workflow.trigger_type == trigger_type.strip(),
                    Workflow.is_active.is_(True),
                )
                .order_by(Workflow.created_at.desc())
            )
            workflows = result.scalars().all()

            return {
                "success": True,
                "status": "matched",
                "workflows": [
                    {
                        "id": workflow.id,
                        "org_id": workflow.org_id,
                        "name": workflow.name,
                        "trigger_type": workflow.trigger_type,
                        "actions": workflow.actions,
                        "is_active": workflow.is_active,
                    }
                    for workflow in workflows
                ],
                "count": len(workflows),
            }

        if db is not None:
            return await _query(db)

        async with async_session_factory() as session:
            return await _query(session)

    @staticmethod
    async def execute(
        workflow_id: str,
        context: Dict[str, Any] | None,
    ) -> Dict[str, Any]:
        context = context or {}

        org_id = context.get("org_id")
        if not org_id:
            return {
                "success": False,
                "status": "invalid_execution_context",
                "workflow_id": workflow_id,
            }

        if not isinstance(workflow_id, str) or not workflow_id.strip():
            return {
                "success": False,
                "status": "invalid_parameters",
                "workflow_id": workflow_id,
            }

        async with async_session_factory() as db:
            result = await db.execute(
                select(Workflow).where(
                    Workflow.id == workflow_id.strip(),
                    Workflow.org_id == org_id,
                )
            )
            workflow = result.scalar_one_or_none()

            if workflow is None:
                return {
                    "success": False,
                    "status": "not_found",
                    "workflow_id": workflow_id.strip(),
                    "org_id": org_id,
                }

            if not workflow.is_active:
                return {
                    "success": False,
                    "status": "workflow_inactive",
                    "workflow_id": workflow.id,
                    "org_id": workflow.org_id,
                }

            actions = workflow.actions

            if not isinstance(actions, list):
                return {
                    "success": False,
                    "status": "invalid_actions",
                    "workflow_id": workflow.id,
                    "org_id": workflow.org_id,
                }

            for action in actions:
                if not isinstance(action, dict):
                    return {
                        "success": False,
                        "status": "invalid_action",
                        "workflow_id": workflow.id,
                        "org_id": workflow.org_id,
                    }

                if (
                    action.get("type") != "notify"
                    or action.get("channel") != "email"
                ):
                    return {
                        "success": False,
                        "status": "unsupported_action",
                        "workflow_id": workflow.id,
                        "org_id": workflow.org_id,
                    }

                for field in ("to", "subject", "body"):
                    value = action.get(field)
                    if not isinstance(value, str) or not value.strip():
                        return {
                            "success": False,
                            "status": "invalid_action",
                            "workflow_id": workflow.id,
                            "org_id": org_id,
                        }

            workflow_data = {
                "id": workflow.id,
                "org_id": workflow.org_id,
                "name": workflow.name,
                "trigger_type": workflow.trigger_type,
                "actions": [dict(action) for action in actions],
                "is_active": workflow.is_active,
            }

        results = []

        for action in workflow_data["actions"]:
            integration = EmailIntegration()

            result = await integration.send_email(
                to=action["to"].strip(),
                subject=action["subject"].strip(),
                body=action["body"],
                html=action.get("html"),
            )

            action_result = {
                "type": action["type"],
                "channel": action["channel"],
                "success": result.success,
            }

            if result.error:
                action_result["error"] = result.error

            results.append(action_result)

            if not result.success:
                return {
                    "success": False,
                    "status": "action_failed",
                    "workflow_id": workflow_data["id"],
                    "org_id": org_id,
                    "results": results,
                }

        return {
            "success": True,
            "status": "executed",
            "workflow_id": workflow_data["id"],
            "org_id": org_id,
            "results": results,
            "workflow": workflow_data,
        }

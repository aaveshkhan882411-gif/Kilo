from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional, Set

from sqlalchemy import select

from app.agents.contracts import AGENT_CONTRACTS
from app.database import async_session_factory
from app.integrations.email import EmailIntegration
from app.models import Lead


ToolHandler = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, ToolHandler] = {}

    def register(self, name: str, handler: ToolHandler) -> None:
        if not name:
            raise ValueError("Tool name is required")
        self._tools[name] = handler

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    def allowed_tools_for_agent(self, agent_id: str) -> Set[str]:
        contract = AGENT_CONTRACTS.get(agent_id)
        if contract is None:
            return set()
        return set(contract.allowed_tools)

    def can_execute(
        self,
        agent_id: str,
        tool: str,
        permissions: list[str],
    ) -> bool:
        contract = AGENT_CONTRACTS.get(agent_id)

        if contract is None:
            return False

        if tool not in contract.allowed_tools:
            return False

        permission_set = set(permissions)

        if "read_all" in permission_set:
            return True

        return all(
            permission in permission_set
            for permission in contract.required_permissions
        )

    async def execute(
        self,
        agent_id: str,
        tool: str,
        params: Dict[str, Any],
        permissions: list[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.can_execute(agent_id, tool, permissions):
            return {
                "success": False,
                "status": "permission_denied",
                "tool": tool,
                "error": "Tool is not allowed for this agent or required permissions are missing",
            }

        if context is None:
            return {
                "success": False,
                "status": "execution_context_required",
                "tool": tool,
                "error": "Trusted execution context is required",
            }

        if not context.get("org_id"):
            return {
                "success": False,
                "status": "invalid_execution_context",
                "tool": tool,
                "error": "Execution context must contain org_id",
            }

        handler = self._tools.get(tool)

        if handler is None:
            return {
                "success": False,
                "status": "tool_not_registered",
                "tool": tool,
                "error": "Tool is allowed by the agent contract but has no registered executor",
            }

        try:
            result = await handler(
                {
                    **params,
                    "_execution_context": context,
                }
            )

            if not isinstance(result, dict):
                return {
                    "success": False,
                    "status": "invalid_tool_result",
                    "tool": tool,
                    "error": "Tool executor must return a dictionary",
                }

            return result

        except Exception:
            return {
                "success": False,
                "status": "tool_execution_failed",
                "tool": tool,
                "error": "Tool executor failed",
            }


async def _crm_lead_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read-only CRM lead tool.

    Security boundary:
    - org_id comes only from the trusted execution context.
    - The model cannot select the tenant.
    - No write operation is exposed.
    """

    context = params.get("_execution_context")

    if not isinstance(context, dict):
        return {
            "success": False,
            "status": "invalid_execution_context",
            "error": "Trusted execution context is required",
        }

    org_id = context.get("org_id")

    if not isinstance(org_id, str) or not org_id:
        return {
            "success": False,
            "status": "invalid_execution_context",
            "error": "Execution context must contain a valid org_id",
        }

    action = params.get("action", "list_leads")

    if action not in {"list_leads", "get_lead"}:
        return {
            "success": False,
            "status": "invalid_tool_action",
            "error": "CRM tool supports only list_leads and get_lead",
        }

    async with async_session_factory() as db:
        if action == "get_lead":
            lead_id = params.get("lead_id")

            if not isinstance(lead_id, str) or not lead_id:
                return {
                    "success": False,
                    "status": "invalid_parameters",
                    "error": "lead_id is required for get_lead",
                }

            result = await db.execute(
                select(Lead).where(
                    Lead.id == lead_id,
                    Lead.org_id == org_id,
                )
            )

            lead = result.scalar_one_or_none()

            if lead is None:
                return {
                    "success": False,
                    "status": "not_found",
                    "error": "Lead not found",
                }

            return {
                "success": True,
                "status": "executed",
                "tool": "crm",
                "action": "get_lead",
                "lead": {
                    "id": lead.id,
                    "first_name": lead.first_name,
                    "last_name": lead.last_name,
                    "email": lead.email,
                    "phone": lead.phone,
                    "company": lead.company,
                    "source": lead.source,
                    "status": lead.status,
                    "score": lead.score,
                    "notes": lead.notes,
                    "created_at": lead.created_at.isoformat(),
                    "updated_at": lead.updated_at.isoformat(),
                },
            }

        raw_limit = params.get("limit", 20)

        try:
            limit = int(raw_limit)
        except (TypeError, ValueError):
            limit = 20

        limit = max(1, min(limit, 50))

        result = await db.execute(
            select(Lead)
            .where(Lead.org_id == org_id)
            .order_by(Lead.created_at.desc())
            .limit(limit)
        )

        leads = result.scalars().all()

        return {
            "success": True,
            "status": "executed",
            "tool": "crm",
            "action": "list_leads",
            "count": len(leads),
            "leads": [
                {
                    "id": lead.id,
                    "first_name": lead.first_name,
                    "last_name": lead.last_name,
                    "email": lead.email,
                    "phone": lead.phone,
                    "company": lead.company,
                    "source": lead.source,
                    "status": lead.status,
                    "score": lead.score,
                    "notes": lead.notes,
                    "created_at": lead.created_at.isoformat(),
                    "updated_at": lead.updated_at.isoformat(),
                }
                for lead in leads
            ],
        }


async def _email_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Production email tool backed by the existing EmailIntegration.

    Security boundary:
    - The execution context is trusted runtime data.
    - The model cannot select or modify the tenant context.
    - Email sending still requires the agent contract's send_email permission.
    - SMTP credentials remain inside EmailIntegration/settings.
    """
    context = params.get("_execution_context")

    if not isinstance(context, dict):
        return {
            "success": False,
            "status": "invalid_execution_context",
            "error": "Trusted execution context is required",
        }

    org_id = context.get("org_id")

    if not isinstance(org_id, str) or not org_id:
        return {
            "success": False,
            "status": "invalid_execution_context",
            "error": "Execution context must contain a valid org_id",
        }

    to = params.get("to")
    subject = params.get("subject")
    body = params.get("body")
    html = params.get("html")

    if not isinstance(to, str) or not to.strip():
        return {
            "success": False,
            "status": "invalid_parameters",
            "tool": "email",
            "error": "to is required",
        }

    if not isinstance(subject, str) or not subject.strip():
        return {
            "success": False,
            "status": "invalid_parameters",
            "tool": "email",
            "error": "subject is required",
        }

    if not isinstance(body, str) or not body.strip():
        return {
            "success": False,
            "status": "invalid_parameters",
            "tool": "email",
            "error": "body is required",
        }

    if html is not None and not isinstance(html, str):
        return {
            "success": False,
            "status": "invalid_parameters",
            "tool": "email",
            "error": "html must be a string when provided",
        }

    integration = EmailIntegration()

    result = await integration.send_email(
        to=to.strip(),
        subject=subject.strip(),
        body=body,
        html=html,
    )

    if not result.success:
        return {
            "success": False,
            "status": "email_send_failed",
            "tool": "email",
            "error": result.error or "Email delivery failed",
        }

    return {
        "success": True,
        "status": "executed",
        "tool": "email",
        "data": result.data or {},
    }


tool_registry = ToolRegistry()

# Built-in production tools.
tool_registry.register("crm", _crm_lead_tool)
tool_registry.register("email", _email_tool)

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional, Set

from app.agents.contracts import AGENT_CONTRACTS


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


tool_registry = ToolRegistry()

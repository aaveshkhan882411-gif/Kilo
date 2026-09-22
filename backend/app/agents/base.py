from datetime import datetime, timezone
from typing import Any, Dict, Optional, List

from app.agents.contracts import AGENT_CONTRACTS, AgentContract


class BaseAgent:
    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name

    def get_contract(self) -> Optional[AgentContract]:
        return AGENT_CONTRACTS.get(self.agent_id)

    async def receive_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "task_id": task.get("task_id"),
            "agent_id": self.agent_id,
            "status": "received",
            "input": task.get("input", {}),
            "context": task.get("context", {}),
            "permissions": task.get("permissions", []),
        }

    async def load_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return context

    async def reason(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "reasoning": "Agent reasoning is not implemented by a model runtime yet.",
            "context": context,
        }

    async def create_plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "plan": [],
            "requested_tool": None,
            "parameters": {},
        }

    async def check_permissions(self, context: Dict[str, Any]) -> bool:
        contract = self.get_contract()
        if contract is None:
            return False

        permissions = set(context.get("permissions", []))

        if "read_all" in permissions:
            return True

        return all(
            permission in permissions
            for permission in contract.required_permissions
        )

    async def request_authorization(
        self,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "authorized": False,
            "reason": "Explicit authorization is required before execution.",
        }

    async def execute_tool(
        self,
        tool: str,
        params: Dict[str, Any],
    ) -> Dict[str, Any]:
        contract = self.get_contract()

        if contract is None:
            return {
                "success": False,
                "error": "Agent contract not found",
            }

        if tool not in contract.allowed_tools:
            return {
                "success": False,
                "error": f"Tool '{tool}' is not allowed for agent '{self.agent_id}'",
            }

        # A real tool registry/executor is not wired yet.
        # Do not pretend that a tool was executed.
        return {
            "success": False,
            "status": "tool_not_implemented",
            "tool": tool,
            "error": "Tool execution backend is not implemented yet",
            "params": params,
        }

    async def verify_result(self, result: Dict[str, Any]) -> bool:
        return bool(result.get("success"))

    async def record_outcome(
        self,
        outcome: Dict[str, Any],
    ) -> Dict[str, Any]:
        return outcome

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        started_at = datetime.now(timezone.utc)

        received_task = await self.receive_task(task)

        contract = self.get_contract()
        if contract is None:
            return {
                "task_id": task.get("task_id"),
                "agent_id": self.agent_id,
                "status": "failed",
                "error": "Agent contract not found",
            }

        context = dict(received_task.get("context", {}))
        context["permissions"] = received_task.get("permissions", [])
        context["input"] = received_task.get("input", {})
        context["task_id"] = received_task.get("task_id")

        context = await self.load_context(context)
        reasoning = await self.reason(context)
        plan = await self.create_plan(reasoning)

        permission_context = {
            **context,
            "plan": plan,
        }

        authorized = await self.check_permissions(permission_context)

        if not authorized:
            auth_result = await self.request_authorization(permission_context)

            if not auth_result.get("authorized"):
                return {
                    "task_id": task.get("task_id"),
                    "agent_id": self.agent_id,
                    "status": "denied",
                    "reason": "required_permissions_missing",
                }

        requested_tool = plan.get("requested_tool")
        parameters = plan.get("parameters", {})

        if requested_tool is None:
            result = {
                "success": False,
                "status": "no_tool_requested",
                "error": "No executable tool was requested by the agent plan",
            }
        else:
            result = await self.execute_tool(
                requested_tool,
                parameters,
            )

        verified = await self.verify_result(result)
        outcome = await self.record_outcome(result)

        elapsed_ms = int(
            (
                datetime.now(timezone.utc) - started_at
            ).total_seconds()
            * 1000
        )

        if not verified:
            return {
                "task_id": task.get("task_id"),
                "agent_id": self.agent_id,
                "status": "failed",
                "result": outcome,
                "execution_time_ms": elapsed_ms,
            }

        return {
            "task_id": task.get("task_id"),
            "agent_id": self.agent_id,
            "status": "completed",
            "result": outcome,
            "execution_time_ms": elapsed_ms,
        }

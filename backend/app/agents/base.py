import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional, List

from app.agents.contracts import AGENT_CONTRACTS, AgentContract
from app.agents.tool_registry import tool_registry
from app.ai.router import ModelRouter


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
        contract = self.get_contract()

        if contract is None:
            return {
                "error": "Agent contract not found",
                "model_response": "",
            }

        model_context = {
            "input": context.get("input", {}),
            "agent": {
                "id": self.agent_id,
                "name": self.name,
            },
            "contract": {
                "allowed_tools": list(contract.allowed_tools),
                "required_permissions": list(contract.required_permissions),
                "capabilities": list(contract.capabilities),
            },
        }

        try:
            response = await ModelRouter.complete(
                prompt="",
                agent_id=self.agent_id,
                max_tokens=1024,
                temperature=0.2,
                context=model_context,
            )

            if not isinstance(response, dict):
                return {
                    "error": "Invalid model response",
                    "model_response": "",
                }

            if response.get("error"):
                return {
                    "error": response.get("error"),
                    "model_response": "",
                }

            return {
                "reasoning": response.get("text", ""),
                "model": response.get("model"),
                "tokens_used": response.get("tokens_used"),
                "model_response": response.get("text", ""),
            }

        except Exception:
            return {
                "error": "Model runtime failed",
                "model_response": "",
            }

    async def create_plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raw_response = context.get("model_response") or context.get("reasoning", "")

        if not isinstance(raw_response, str) or not raw_response.strip():
            return {
                "plan": [],
                "requested_tool": None,
                "parameters": {},
            }

        content = raw_response.strip()

        if content.startswith("```") and content.endswith("```"):
            lines = content.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines).strip()

        try:
            parsed = json.loads(content)
        except (TypeError, ValueError):
            return {
                "plan": [],
                "requested_tool": None,
                "parameters": {},
            }

        if not isinstance(parsed, dict):
            return {
                "plan": [],
                "requested_tool": None,
                "parameters": {},
            }

        requested_tool = parsed.get("requested_tool")

        if requested_tool is not None and not isinstance(requested_tool, str):
            requested_tool = None

        parameters = parsed.get("parameters", {})

        if not isinstance(parameters, dict):
            parameters = {}

        contract = self.get_contract()

        if (
            requested_tool is not None
            and (
                contract is None
                or requested_tool not in contract.allowed_tools
            )
        ):
            requested_tool = None
            parameters = {}

        blocked_keys = {
            "org_id",
            "user_id",
            "permissions",
            "authorization",
            "authorization_token",
            "access_token",
            "refresh_token",
            "token",
            "api_key",
        }

        parameters = {
            key: value
            for key, value in parameters.items()
            if key not in blocked_keys
        }

        return {
            "plan": parsed.get("plan", []),
            "requested_tool": requested_tool,
            "parameters": parameters,
            "reasoning": parsed.get("reasoning", ""),
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
        permissions: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return await tool_registry.execute(
            agent_id=self.agent_id,
            tool=tool,
            params=params,
            permissions=permissions or [],
            context=context,
        )

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

        planning_context = {
            **context,
            **reasoning,
        }

        plan = await self.create_plan(planning_context)

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
                context.get("permissions", []),
                context,
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

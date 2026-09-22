from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.registry import registry
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.ai import AICompletionRequest, AICompletionResponse
from app.schemas.agent import AgentTask

router = APIRouter()


@router.get("/agents", response_model=list[dict])
async def list_agents(
    current_user: User = Depends(get_current_active_user),
):
    return registry.list_agents()


@router.post("/agents/{agent_id}/execute", response_model=dict)
async def execute_agent(
    agent_id: str,
    task: AgentTask,
    current_user: User = Depends(get_current_active_user),
):
    if agent_id != task.agent_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent ID mismatch",
        )

    if task.org_id != current_user.org_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Task does not belong to the current organization",
        )

    agent = registry.get(agent_id)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    contract = registry.get_contract(agent_id)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent contract not found",
        )

    missing_permissions = [
        permission
        for permission in contract.required_permissions
        if permission not in task.permissions
    ]

    if missing_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Required agent permissions are missing",
                "missing_permissions": missing_permissions,
            },
        )

    if task.authorization_required:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Explicit authorization is required before agent execution",
        )

    return {
        "agent_id": agent_id,
        "task_id": task.task_id,
        "status": "validated",
        "result": {
            "message": "Agent execution request passed authorization checks",
        },
    }


@router.post("/completions", response_model=AICompletionResponse)
async def ai_completion(
    request: AICompletionRequest,
    current_user: User = Depends(get_current_active_user),
):
    return AICompletionResponse(
        text="Mock response",
        model="mock",
        tokens_used=10,
        finish_reason="stop",
        agent_id=request.agent_id,
    )

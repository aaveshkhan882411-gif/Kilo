from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.ai import AICompletionRequest, AICompletionResponse
from app.agents.registry import AgentRegistry

router = APIRouter()


@router.get("/agents", response_model=list[dict])
async def list_agents(current_user: User = Depends(get_current_active_user)):
    registry = AgentRegistry()
    return registry.list_agents()


@router.post("/agents/{agent_id}/execute", response_model=dict)
async def execute_agent(agent_id: str, task: dict, current_user: User = Depends(get_current_active_user)):
    registry = AgentRegistry()
    return {"agent_id": agent_id, "status": "executed", "result": {}}


@router.post("/completions", response_model=AICompletionResponse)
async def ai_completion(
    request: AICompletionRequest,
    current_user: User = Depends(get_current_active_user),
):
    return AICompletionResponse(text="Mock response", model="mock", tokens_used=10, finish_reason="stop")

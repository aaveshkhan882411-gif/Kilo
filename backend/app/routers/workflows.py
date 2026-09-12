from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_active_user
from app.schemas.workflow import WorkflowCreate, WorkflowResponse

router = APIRouter()


@router.post("/", response_model=WorkflowResponse, status_code=201)
async def create_workflow(workflow_in: WorkflowCreate, current_user: User = Depends(get_current_active_user)):
    pass


@router.get("/", response_model=list[WorkflowResponse])
async def list_workflows(current_user: User = Depends(get_current_active_user)):
    pass

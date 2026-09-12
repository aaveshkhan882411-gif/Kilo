from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_active_user
from app.schemas.task import TaskCreate, TaskResponse
from app.schemas.appointment import AppointmentCreate, AppointmentResponse

router = APIRouter()


@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def create_task(task_in: TaskCreate, current_user: User = Depends(get_current_active_user)):
    pass


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(current_user: User = Depends(get_current_active_user)):
    pass


@router.post("/appointments", response_model=AppointmentResponse, status_code=201)
async def create_appointment(appt_in: AppointmentCreate, current_user: User = Depends(get_current_active_user)):
    pass


@router.get("/appointments", response_model=list[AppointmentResponse])
async def list_appointments(current_user: User = Depends(get_current_active_user)):
    pass

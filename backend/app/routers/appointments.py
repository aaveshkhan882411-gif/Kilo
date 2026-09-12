from fastapi import APIRouter, Depends
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def create_appointment(appt_in: AppointmentCreate, current_user: User = Depends(get_current_active_user)):
    pass


@router.get("/", response_model=list[AppointmentResponse])
async def list_appointments(current_user: User = Depends(get_current_active_user)):
    pass

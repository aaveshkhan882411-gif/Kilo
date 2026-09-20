from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models import Appointment, Lead
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.services.audit_service import AuditService

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appt_in: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    organizer_result = await db.execute(
        select(User).where(
            User.id == appt_in.organizer_id,
            User.org_id == current_user.org_id,
            User.is_active.is_(True),
        )
    )
    organizer = organizer_result.scalar_one_or_none()

    if organizer is None:
        raise HTTPException(status_code=404, detail="Organizer not found")

    if appt_in.attendee_id:
        attendee_result = await db.execute(
            select(User).where(
                User.id == appt_in.attendee_id,
                User.org_id == current_user.org_id,
                User.is_active.is_(True),
            )
        )
        if attendee_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Attendee not found")

    if appt_in.lead_id:
        lead_result = await db.execute(
            select(Lead).where(
                Lead.id == appt_in.lead_id,
                Lead.org_id == current_user.org_id,
            )
        )
        if lead_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Lead not found")

    appointment = Appointment(
        **appt_in.model_dump(),
        org_id=current_user.org_id,
    )

    db.add(appointment)
    await db.flush()

    await AuditService.record(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="CREATE",
        entity_type="appointment",
        entity_id=appointment.id,
        changes=appt_in.model_dump(mode="json"),
    )

    await db.commit()
    await db.refresh(appointment)

    return appointment


@router.get("/", response_model=list[AppointmentResponse])
async def list_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Appointment)
        .where(Appointment.org_id == current_user.org_id)
        .order_by(Appointment.start_time.asc())
    )

    return result.scalars().all()

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models import Lead, Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter()


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if task_in.assigned_user_id:
        assigned_result = await db.execute(
            select(User).where(
                User.id == task_in.assigned_user_id,
                User.org_id == current_user.org_id,
                User.is_active.is_(True),
            )
        )
        if assigned_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Assigned user not found")

    if task_in.lead_id:
        lead_result = await db.execute(
            select(Lead).where(
                Lead.id == task_in.lead_id,
                Lead.org_id == current_user.org_id,
            )
        )
        if lead_result.scalar_one_or_none() is None:
            raise HTTPException(status_code=404, detail="Lead not found")

    task = Task(
        **task_in.model_dump(),
        org_id=current_user.org_id,
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task


@router.get("/tasks", response_model=list[TaskResponse])
async def list_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Task)
        .where(Task.org_id == current_user.org_id)
        .order_by(Task.created_at.desc())
    )

    return result.scalars().all()

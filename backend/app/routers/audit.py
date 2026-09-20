from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_superuser
from app.database import get_db
from app.models import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogFilter, AuditLogResponse

router = APIRouter()


@router.get("/", response_model=list[AuditLogResponse])
async def list_audit_logs(
    filters: AuditLogFilter = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    query = select(AuditLog).where(
        AuditLog.org_id == current_user.org_id
    )

    if filters.action:
        query = query.where(AuditLog.action == filters.action)

    if filters.entity_type:
        query = query.where(AuditLog.entity_type == filters.entity_type)

    if filters.entity_id:
        query = query.where(AuditLog.entity_id == filters.entity_id)

    if filters.user_id:
        query = query.where(AuditLog.user_id == filters.user_id)

    if filters.start_date:
        query = query.where(AuditLog.created_at >= filters.start_date)

    if filters.end_date:
        query = query.where(AuditLog.created_at <= filters.end_date)

    page = max(filters.page, 1)
    size = min(max(filters.size, 1), 100)

    query = (
        query
        .order_by(AuditLog.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )

    result = await db.execute(query)
    return result.scalars().all()

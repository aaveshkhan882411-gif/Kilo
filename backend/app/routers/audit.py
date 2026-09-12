from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_superuser
from app.schemas.audit_log import AuditLogFilter, AuditLogResponse

router = APIRouter()


@router.get("/", response_model=list[AuditLogResponse])
async def list_audit_logs(
    filters: AuditLogFilter = Depends(),
    current_user: User = Depends(get_current_superuser),
):
    return []

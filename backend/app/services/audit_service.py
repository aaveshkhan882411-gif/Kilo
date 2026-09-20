from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog


class AuditService:
    @staticmethod
    async def record(
        db: AsyncSession,
        org_id: str,
        user_id: Optional[str],
        action: str,
        entity_type: str,
        entity_id: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        audit_log = AuditLog(
            org_id=org_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        db.add(audit_log)
        await db.flush()

        return audit_log

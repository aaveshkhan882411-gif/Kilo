from datetime import datetime
from typing import Dict, Any, List, Optional


class AuditService:
    @staticmethod
    def record(org_id: str, user_id: Optional[str], action: str, entity_type: str, entity_id: Optional[str], changes: Optional[Dict[str, Any]], ip_address: Optional[str], user_agent: Optional[str]) -> Dict[str, Any]:
        return {
            "org_id": org_id,
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "changes": changes,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.utcnow().isoformat(),
        }

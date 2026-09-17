from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class OutcomeLifecycleStatus(str, Enum):
    REQUESTED = "REQUESTED"
    PLANNED = "PLANNED"
    AUTHORIZED = "AUTHORIZED"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    OUTCOME_RECORDED = "OUTCOME_RECORDED"


class TechnicalStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


class BusinessStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    UNKNOWN = "unknown"


class OutcomeEngine:
    VALID_TRANSITIONS = {
        OutcomeLifecycleStatus.REQUESTED: [OutcomeLifecycleStatus.PLANNED],
        OutcomeLifecycleStatus.PLANNED: [OutcomeLifecycleStatus.AUTHORIZED],
        OutcomeLifecycleStatus.AUTHORIZED: [OutcomeLifecycleStatus.EXECUTING],
        OutcomeLifecycleStatus.EXECUTING: [OutcomeLifecycleStatus.EXECUTED, OutcomeLifecycleStatus.FAILED],
        OutcomeLifecycleStatus.EXECUTED: [OutcomeLifecycleStatus.VERIFIED],
        OutcomeLifecycleStatus.VERIFIED: [OutcomeLifecycleStatus.OUTCOME_RECORDED],
    }

    @classmethod
    def transition(cls, current: str, next_status: str) -> bool:
        current_enum = OutcomeLifecycleStatus(current)
        next_enum = OutcomeLifecycleStatus(next_status)
        return next_enum in cls.VALID_TRANSITIONS.get(current_enum, [])

    @classmethod
    def record(cls, entity_type: str, entity_id: str, technical_status: str, business_status: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "lifecycle_status": OutcomeLifecycleStatus.OUTCOME_RECORDED.value,
            "technical_status": technical_status,
            "business_status": business_status or BusinessStatus.UNKNOWN.value,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

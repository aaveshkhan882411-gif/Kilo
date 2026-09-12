from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from .base import BaseAgent
from .contracts import AGENT_CONTRACTS, AgentContract


class GIPEvent:
    def __init__(self, event_type: str, agent_id: Optional[str], task_id: Optional[str], payload: Dict[str, Any]):
        self.event_type = event_type
        self.agent_id = agent_id
        self.task_id = task_id
        self.payload = payload
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }


class GIPEventBus:
    EVENT_TYPES = [
        "TASK_CREATED", "TASK_ASSIGNED", "TASK_STARTED", "AUTHORIZATION_REQUIRED",
        "AUTHORIZATION_GRANTED", "AUTHORIZATION_DENIED", "ACTION_STARTED", "ACTION_COMPLETED",
        "ACTION_FAILED", "LEAD_CREATED", "LEAD_QUALIFIED", "APPOINTMENT_REQUESTED",
        "APPOINTMENT_BOOKED", "FOLLOWUP_REQUIRED", "PAYMENT_VERIFIED", "WORKFORCE_DEPLOYED",
        "OUTCOME_RECORDED", "ERROR", "RECOVERY_STARTED", "RECOVERY_COMPLETED",
    ]

    def __init__(self):
        self._subscribers: List[Callable[[GIPEvent], None]] = []

    def subscribe(self, callback: Callable[[GIPEvent], None]):
        self._subscribers.append(callback)

    def publish(self, event_type: str, agent_id: Optional[str], task_id: Optional[str], payload: Dict[str, Any]):
        event = GIPEvent(event_type, agent_id, task_id, payload)
        for callback in self._subscribers:
            callback(event)
        return event


gip_bus = GIPEventBus()

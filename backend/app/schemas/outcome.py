from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class OutcomeResponse(BaseModel):
    id: str
    org_id: str
    entity_type: str
    entity_id: str
    lifecycle_status: str
    technical_status: str
    business_status: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OutcomeLifecycleUpdate(BaseModel):
    lifecycle_status: str
    technical_status: str
    business_status: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

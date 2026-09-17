from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class IntegrationCreate(BaseModel):
    provider: str = Field(..., max_length=50)
    config: Dict[str, Any] = {}


class IntegrationUpdate(BaseModel):
    config: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class IntegrationResponse(BaseModel):
    id: str
    org_id: str
    provider: str
    config: Dict[str, Any]
    status: str
    last_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

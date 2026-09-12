from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ActivityCreate(BaseModel):
    type: str = Field(..., max_length=50)
    subject: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    user_id: Optional[str] = None
    lead_id: Optional[str] = None
    contact_id: Optional[str] = None
    deal_id: Optional[str] = None


class ActivityResponse(BaseModel):
    id: str
    org_id: str
    type: str
    subject: str
    description: Optional[str] = None
    user_id: Optional[str] = None
    lead_id: Optional[str] = None
    contact_id: Optional[str] = None
    deal_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

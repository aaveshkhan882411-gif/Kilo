from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CustomerCreate(BaseModel):
    contact_id: str
    company_id: Optional[str] = None
    status: str = "active"
    lifetime_value: float = 0.0


class CustomerResponse(BaseModel):
    id: str
    org_id: str
    contact_id: str
    company_id: Optional[str] = None
    status: str
    lifetime_value: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

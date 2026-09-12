from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    trigger_type: str = Field(..., max_length=50)
    actions: list = Field(..., min_length=1)
    is_active: bool = True


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    trigger_type: Optional[str] = Field(None, max_length=50)
    actions: Optional[list] = None
    is_active: Optional[bool] = None


class WorkflowResponse(BaseModel):
    id: str
    org_id: str
    name: str
    trigger_type: str
    actions: list
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DealCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    company_id: str
    contact_id: str
    value: float = Field(..., gt=0)
    stage: str = "qualification"
    probability: int = Field(0, ge=0, le=100)
    expected_close_date: Optional[datetime] = None


class DealUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    value: Optional[float] = Field(None, gt=0)
    stage: Optional[str] = None
    probability: Optional[int] = Field(None, ge=0, le=100)
    expected_close_date: Optional[datetime] = None


class DealStageUpdate(BaseModel):
    stage: str
    probability: Optional[int] = Field(None, ge=0, le=100)


class DealResponse(BaseModel):
    id: str
    org_id: str
    title: str
    company_id: str
    contact_id: str
    value: float
    stage: str
    probability: int
    expected_close_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

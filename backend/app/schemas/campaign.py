from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CampaignCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., max_length=50)
    status: str = "draft"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = Field(None, gt=0)


class CampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = Field(None, gt=0)


class CampaignResponse(BaseModel):
    id: str
    org_id: str
    name: str
    type: str
    status: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    budget: Optional[float] = None
    spent: float
    leads_generated: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

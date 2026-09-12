from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LeadCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)
    source: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=255)
    source: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = None
    score: Optional[int] = None
    notes: Optional[str] = None


class LeadResponse(BaseModel):
    id: str
    org_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    company: Optional[str] = None
    source: Optional[str] = None
    status: str
    score: int
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadScoreResponse(BaseModel):
    lead_id: str
    score: int
    reasoning: str

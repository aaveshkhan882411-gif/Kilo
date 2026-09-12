from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    size: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    annual_revenue: Optional[float] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    size: Optional[str] = Field(None, max_length=50)
    location: Optional[str] = Field(None, max_length=255)
    annual_revenue: Optional[float] = None


class CompanyResponse(BaseModel):
    id: str
    org_id: str
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    annual_revenue: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

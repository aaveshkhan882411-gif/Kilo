from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class PaymentCreate(BaseModel):
    subscription_id: Optional[str] = None
    amount: float = Field(..., gt=0)
    currency: str = "USD"
    paypal_order_id: Optional[str] = None
    paypal_capture_id: Optional[str] = None


class PaymentResponse(BaseModel):
    id: str
    org_id: str
    subscription_id: Optional[str] = None
    amount: float
    currency: str
    status: str
    paypal_order_id: Optional[str] = None
    paypal_capture_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PayPalOrderResponse(BaseModel):
    order_id: str
    status: str
    links: list[Dict[str, str]]


class PayPalCaptureResponse(BaseModel):
    capture_id: str
    status: str
    amount: float
    currency: str

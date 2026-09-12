from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class WebsiteAnalysisRequest(BaseModel):
    url: str = Field(..., min_length=1, max_length=2048)
    analysis_depth: str = "standard"


class WebsiteAnalysisResponse(BaseModel):
    url: str
    analyzed_at: datetime
    business_name: Optional[str] = None
    products: List[str] = []
    services: List[str] = []
    pricing: Optional[str] = None
    locations: List[str] = []
    contact_methods: List[str] = []
    faqs: List[Dict[str, str]] = []
    ctas: List[str] = []
    navigation: List[str] = []
    testimonials: List[Dict[str, str]] = []
    structured_data: Dict[str, Any] = {}
    opportunities: List[str] = []
    bottlenecks: List[str] = []
    raw_text_length: int
    page_count: int


class BusinessIntelligence(BaseModel):
    industry: str
    products: List[str]
    services: List[str]
    target_customers: str
    locations: List[str]
    pricing_model: str
    lead_channels: List[str]
    sales_process: str
    customer_journey: str
    business_goals: List[str]
    opportunities: List[str]
    risks: List[str]
    bottlenecks: List[str]


class WorkforceRecommendation(BaseModel):
    recommended_agents: List[str]
    reasoning: str
    estimated_roi: float
    implementation_priority: List[str]
    required_plan: str

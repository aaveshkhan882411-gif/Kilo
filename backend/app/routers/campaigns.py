from app.models.user import User
from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_active_user
from app.schemas.campaign import CampaignCreate, CampaignResponse

router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=201)
async def create_campaign(campaign_in: CampaignCreate, current_user: User = Depends(get_current_active_user)):
    pass


@router.get("/", response_model=list[CampaignResponse])
async def list_campaigns(current_user: User = Depends(get_current_active_user)):
    pass

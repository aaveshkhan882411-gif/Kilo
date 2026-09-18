from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models import Campaign
from app.models.user import User
from app.schemas.campaign import CampaignCreate, CampaignResponse

router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_in: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    campaign = Campaign(
        **campaign_in.model_dump(),
        org_id=current_user.org_id,
        spent=0,
        leads_generated=0,
    )

    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    return campaign


@router.get("/", response_model=list[CampaignResponse])
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Campaign)
        .where(Campaign.org_id == current_user.org_id)
        .order_by(Campaign.created_at.desc())
    )

    return result.scalars().all()

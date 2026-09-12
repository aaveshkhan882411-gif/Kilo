from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadScoreResponse
from app.models.lead import Lead
from app.auth.dependencies import get_current_active_user

router = APIRouter()


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_in: LeadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    lead = Lead(
        **lead_in.model_dump(),
        org_id=current_user.org_id,
    )
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.get("/", response_model=list[LeadResponse])
async def list_leads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Lead).where(Lead.org_id == current_user.org_id).order_by(Lead.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.org_id == current_user.org_id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    lead_in: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.org_id == current_user.org_id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    for field, value in lead_in.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)
    await db.commit()
    await db.refresh(lead)
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.org_id == current_user.org_id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    await db.delete(lead)
    await db.commit()
    return None


@router.post("/{lead_id}/score", response_model=LeadScoreResponse)
async def score_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.org_id == current_user.org_id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    score = min(100, max(0, 50 + (20 if lead.company else 0) + (15 if lead.phone else 0)))
    lead.score = score
    await db.commit()
    await db.refresh(lead)
    return LeadScoreResponse(lead_id=lead.id, score=score, reasoning="Automated scoring")


@router.post("/{lead_id}/qualify", response_model=LeadResponse)
async def qualify_lead(
    lead_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.org_id == current_user.org_id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.status = "qualified"
    lead.score = min(100, lead.score + 20)
    await db.commit()
    await db.refresh(lead)
    return lead

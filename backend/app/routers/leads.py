from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadScoreResponse
from app.models.lead import Lead
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.services.audit_service import AuditService

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
    await db.flush()

    await AuditService.record(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="CREATE",
        entity_type="lead",
        entity_id=lead.id,
        changes=lead_in.model_dump(),
    )

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

    changes = {}
    for field, value in lead_in.model_dump(exclude_unset=True).items():
        changes[field] = {
            "old": getattr(lead, field),
            "new": value,
        }
        setattr(lead, field, value)

    await db.flush()

    await AuditService.record(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="UPDATE",
        entity_type="lead",
        entity_id=lead.id,
        changes=changes,
    )

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

    await AuditService.record(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="DELETE",
        entity_type="lead",
        entity_id=lead.id,
        changes={
            "first_name": lead.first_name,
            "last_name": lead.last_name,
            "email": lead.email,
            "phone": lead.phone,
            "company": lead.company,
            "source": lead.source,
            "status": lead.status,
            "score": lead.score,
            "notes": lead.notes,
        },
    )

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
    old_score = lead.score
    lead.score = score

    await db.flush()

    await AuditService.record(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="SCORE",
        entity_type="lead",
        entity_id=lead.id,
        changes={
            "score": {
                "old": old_score,
                "new": score,
            },
            "reasoning": "Automated scoring",
        },
    )

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

    old_status = lead.status
    old_score = lead.score
    new_score = min(100, lead.score + 20)

    lead.status = "qualified"
    lead.score = new_score

    await db.flush()

    await AuditService.record(
        db=db,
        org_id=current_user.org_id,
        user_id=current_user.id,
        action="QUALIFY",
        entity_type="lead",
        entity_id=lead.id,
        changes={
            "status": {
                "old": old_status,
                "new": "qualified",
            },
            "score": {
                "old": old_score,
                "new": new_score,
            },
        },
    )

    await db.commit()
    await db.refresh(lead)
    return lead

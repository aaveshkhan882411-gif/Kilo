from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models import Integration
from app.models.user import User
from app.schemas.integration import (
    IntegrationCreate,
    IntegrationUpdate,
    IntegrationResponse,
)

router = APIRouter()


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("/", response_model=list[IntegrationResponse])
async def list_integrations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Integration)
        .where(Integration.org_id == current_user.org_id)
        .order_by(Integration.created_at.desc())
    )

    return result.scalars().all()


@router.post(
    "/",
    response_model=IntegrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_integration(
    integration_in: IntegrationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    integration = Integration(
        org_id=current_user.org_id,
        provider=integration_in.provider,
        config=integration_in.config,
        status="inactive",
    )

    db.add(integration)
    await db.commit()
    await db.refresh(integration)

    return integration


@router.patch("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    integration_id: str,
    integration_in: IntegrationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(Integration).where(
            Integration.id == integration_id,
            Integration.org_id == current_user.org_id,
        )
    )
    integration = result.scalar_one_or_none()

    if integration is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )

    update_data = integration_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(integration, field, value)

    integration.updated_at = utc_now()

    await db.commit()
    await db.refresh(integration)

    return integration

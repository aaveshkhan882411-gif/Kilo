from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.schemas.user import (
    RegistrationCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
)
from app.models.user import User
from app.models.organization import Organization
from app.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.auth.dependencies import get_current_active_user
from app.database import get_db

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_in: RegistrationCreate,
    db: AsyncSession = Depends(get_db),
):
    existing_user = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    existing_org = await db.execute(
        select(Organization).where(
            Organization.slug == user_in.organization_slug
        )
    )
    if existing_org.scalar_one_or_none():
        raise HTTPException(
            status_code=400,
            detail="Organization slug already exists",
        )

    organization = Organization(
        name=user_in.organization_name,
        slug=user_in.organization_slug,
        plan="starter",
    )
    db.add(organization)
    await db.flush()

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role="owner",
        org_id=organization.id,
    )
    db.add(user)

    await db.commit()
    await db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(
        user_in.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(
        data={"sub": user.id, "org_id": user.org_id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.id, "org_id": user.org_id}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_in: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(
        refresh_in.refresh_token,
        expected_type="refresh",
    )

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    access_token = create_access_token(
        data={"sub": user.id, "org_id": user.org_id}
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_in.refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user),
):
    return UserResponse.model_validate(current_user)

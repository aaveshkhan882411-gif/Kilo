from datetime import datetime, timedelta, timezone

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
from app.models import AuthSession
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
from app.config import settings

import hashlib
import uuid


router = APIRouter()


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def refresh_expiry() -> datetime:
    return utc_now() + timedelta(
        days=settings.AUTH_REFRESH_TOKEN_EXPIRE_DAYS
    )


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

    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Inactive user",
        )

    organization_result = await db.execute(
        select(Organization).where(Organization.id == user.org_id)
    )
    organization = organization_result.scalar_one_or_none()

    if not organization or not organization.is_active:
        raise HTTPException(
            status_code=401,
            detail="Inactive organization",
        )

    access_token = create_access_token(
        data={"sub": user.id, "org_id": user.org_id}
    )

    refresh_token = create_refresh_token(
        data={"sub": user.id, "org_id": user.org_id}
    )

    refresh_payload = decode_token(
        refresh_token,
        expected_type="refresh",
    )

    if not refresh_payload or not refresh_payload.get("jti"):
        raise HTTPException(
            status_code=500,
            detail="Failed to create refresh session",
        )

    session_id = refresh_payload["jti"]

    db.add(
        AuthSession(
            id=session_id,
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=refresh_expiry(),
        )
    )

    user.last_login = utc_now()

    await db.commit()
    await db.refresh(user)

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
    session_id = payload.get("jti")

    if not user_id or not session_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    token_hash = hash_refresh_token(refresh_in.refresh_token)

    session_result = await db.execute(
        select(AuthSession)
        .where(
            AuthSession.id == session_id,
            AuthSession.user_id == user_id,
            AuthSession.token_hash == token_hash,
        )
        .with_for_update()
    )
    session = session_result.scalar_one_or_none()

    now = utc_now()

    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh session",
        )

    if session.revoked_at is not None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has been revoked",
        )

    if session.expires_at <= now:
        raise HTTPException(
            status_code=401,
            detail="Refresh session expired",
        )

    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        session.revoked_at = now
        await db.commit()
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )

    if not user.is_active:
        session.revoked_at = now
        await db.commit()
        raise HTTPException(
            status_code=401,
            detail="Inactive user",
        )

    organization_result = await db.execute(
        select(Organization).where(Organization.id == user.org_id)
    )
    organization = organization_result.scalar_one_or_none()

    if not organization or not organization.is_active:
        session.revoked_at = now
        await db.commit()
        raise HTTPException(
            status_code=401,
            detail="Inactive organization",
        )

    session.revoked_at = now

    new_refresh_token = create_refresh_token(
        data={"sub": user.id, "org_id": user.org_id}
    )

    new_payload = decode_token(
        new_refresh_token,
        expected_type="refresh",
    )

    if not new_payload or not new_payload.get("jti"):
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to rotate refresh session",
        )

    new_session_id = new_payload["jti"]

    db.add(
        AuthSession(
            id=new_session_id,
            user_id=user.id,
            token_hash=hash_refresh_token(new_refresh_token),
            expires_at=refresh_expiry(),
        )
    )

    access_token = create_access_token(
        data={"sub": user.id, "org_id": user.org_id}
    )

    await db.commit()
    await db.refresh(user)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_in: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(
        refresh_in.refresh_token,
        expected_type="refresh",
    )

    if not payload:
        return None

    session_id = payload.get("jti")
    user_id = payload.get("sub")

    if not session_id or not user_id:
        return None

    token_hash = hash_refresh_token(refresh_in.refresh_token)

    result = await db.execute(
        select(AuthSession).where(
            AuthSession.id == session_id,
            AuthSession.user_id == user_id,
            AuthSession.token_hash == token_hash,
        )
    )
    session = result.scalar_one_or_none()

    if session and session.revoked_at is None:
        session.revoked_at = utc_now()
        await db.commit()

    return None


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_active_user),
):
    return UserResponse.model_validate(current_user)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.user import User
from app.auth.utils import hash_password
from app.auth.dependencies import get_current_superuser

router = APIRouter()


def validate_target_role(
    current_user: User,
    target_role: str,
) -> None:
    allowed_roles = {"viewer", "admin"}

    if target_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid target role",
        )

    if current_user.role == "admin" and target_role != "viewer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admins can only create or assign viewer users",
        )


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    result = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )

    validate_target_role(current_user, user_in.role)

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        org_id=current_user.org_id,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user


@router.get("/", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    result = await db.execute(
        select(User).where(User.org_id == current_user.org_id)
    )
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.org_id != current_user.org_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.org_id != current_user.org_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    update_data = user_in.model_dump(exclude_unset=True)

    if "role" in update_data:
        validate_target_role(
            current_user,
            update_data["role"],
        )

        if user.role == "owner":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Owner role cannot be changed",
            )

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
):
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if user.org_id != current_user.org_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )

    if user.role == "owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner cannot be deleted",
        )

    await db.delete(user)
    await db.commit()

    return None

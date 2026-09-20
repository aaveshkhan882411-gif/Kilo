from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from ..config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire,
        "token_type": "access",
    })
    return jwt.encode(
        to_encode,
        settings.AUTH_SECRET,
        algorithm=settings.AUTH_ALGORITHM,
    )


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.AUTH_REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({
        "exp": expire,
        "token_type": "refresh",
        "jti": str(uuid4()),
    })
    return jwt.encode(
        to_encode,
        settings.AUTH_SECRET,
        algorithm=settings.AUTH_ALGORITHM,
    )


def decode_token(
    token: str,
    expected_type: Optional[str] = None,
) -> Optional[dict]:
    try:
        payload = jwt.decode(
            token,
            settings.AUTH_SECRET,
            algorithms=[settings.AUTH_ALGORITHM],
        )

        if expected_type and payload.get("token_type") != expected_type:
            return None

        return payload
    except JWTError:
        return None

from fastapi import APIRouter, Depends
from app.config import settings
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.integrations.google import GoogleOAuthIntegration

router = APIRouter()


@router.get("/login")
async def google_login():
    google = GoogleOAuthIntegration()
    return {"auth_url": google.get_authorization_url()}


@router.get("/callback")
async def google_callback(code: str, current_user: User = Depends(get_current_active_user)):
    google = GoogleOAuthIntegration()
    tokens = await google.exchange_code(code)
    return {"tokens": tokens}

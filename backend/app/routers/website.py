from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.website import WebsiteAnalysisRequest, WebsiteAnalysisResponse
from app.services.website_analyzer import WebsiteAnalyzer

router = APIRouter()


@router.post("/analyze", response_model=WebsiteAnalysisResponse)
async def analyze_website(
    request: WebsiteAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
):
    analyzer = WebsiteAnalyzer()
    return await analyzer.analyze(request.url)

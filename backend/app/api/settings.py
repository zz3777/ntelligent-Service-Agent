from fastapi import APIRouter

from app.core.config import settings
from app.schemas.settings import LLMSettingsResponse

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("/llm", response_model=LLMSettingsResponse)
async def get_llm_settings():
    masked_key = ""
    if settings.LLM_API_KEY:
        k = settings.LLM_API_KEY
        masked_key = k[:6] + "****" + k[-4:] if len(k) > 10 else "****"
    return LLMSettingsResponse(
        api_key=masked_key,
        base_url=settings.LLM_BASE_URL,
        model=settings.LLM_MODEL,
    )

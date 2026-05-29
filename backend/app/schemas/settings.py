from pydantic import BaseModel


class LLMSettingsResponse(BaseModel):
    api_key: str
    base_url: str
    model: str

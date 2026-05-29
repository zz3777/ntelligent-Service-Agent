from datetime import datetime
from pydantic import BaseModel, field_validator
from uuid import UUID


class ChatRequest(BaseModel):
    conversation_id: UUID | None = None
    message: str
    file_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: UUID
    task_id: str
    reply: str


class ConversationListItem(BaseModel):
    id: UUID
    title: str
    updated_at: str

    model_config = {"from_attributes": True}

    @field_validator("updated_at", mode="before")
    @classmethod
    def convert_datetime(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()
        return v

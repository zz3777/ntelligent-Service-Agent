from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ApprovalOut(BaseModel):
    id: UUID
    task_id: str
    tool_name: str
    params: str | None
    reason: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ApprovalActionRequest(BaseModel):
    comment: str | None = None


class ApprovalListResponse(BaseModel):
    items: list[ApprovalOut]
    total: int

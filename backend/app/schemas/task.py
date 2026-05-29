from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class TaskLogOut(BaseModel):
    id: UUID
    task_id: str
    action: str
    tool_name: str | None
    tool_server: str | None
    status: str
    duration_ms: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskLogDetailOut(TaskLogOut):
    input_params: str | None
    output_summary: str | None
    user_id: UUID | None


class TaskLogListResponse(BaseModel):
    items: list[TaskLogOut]
    total: int

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.db import get_db
from app.schemas.task import TaskLogOut, TaskLogDetailOut, TaskLogListResponse
from app.models.task_log import TaskLog

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=TaskLogListResponse)
async def list_tasks(
    status: str | None = Query(None),
    tool_name: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(TaskLog).order_by(TaskLog.created_at.desc())
    count_query = select(func.count(TaskLog.id))

    if status:
        query = query.where(TaskLog.status == status)
        count_query = count_query.where(TaskLog.status == status)
    if tool_name:
        query = query.where(TaskLog.tool_name == tool_name)
        count_query = count_query.where(TaskLog.tool_name == tool_name)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)

    return TaskLogListResponse(
        items=[TaskLogOut.model_validate(t) for t in result.scalars().all()],
        total=total,
    )


@router.get("/{task_id}", response_model=TaskLogDetailOut)
async def get_task_detail(task_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TaskLog).where(TaskLog.task_id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="任务不存在")
    return TaskLogDetailOut.model_validate(task)

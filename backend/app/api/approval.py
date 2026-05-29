from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.db import get_db
from app.schemas.approval import ApprovalOut, ApprovalActionRequest, ApprovalListResponse
from app.models.approval import Approval

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


@router.get("", response_model=ApprovalListResponse)
async def list_approvals(
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    query = select(Approval).order_by(Approval.created_at.desc())
    count_query = select(func.count(Approval.id))

    if status:
        query = query.where(Approval.status == status)
        count_query = count_query.where(Approval.status == status)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)

    return ApprovalListResponse(
        items=[ApprovalOut.model_validate(a) for a in result.scalars().all()],
        total=total,
    )


@router.post("/{approval_id}/approve")
async def approve(approval_id: str, request: ApprovalActionRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Approval).where(Approval.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="审批不存在")
    approval.status = "approved"
    approval.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "已批准"}


@router.post("/{approval_id}/reject")
async def reject(approval_id: str, request: ApprovalActionRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Approval).where(Approval.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="审批不存在")
    approval.status = "rejected"
    approval.reviewed_at = datetime.now(timezone.utc)
    await db.commit()
    return {"message": "已驳回"}

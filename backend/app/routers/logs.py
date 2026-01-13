from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.request_log import RequestLog
from app.schemas.request_log import RequestLogResponse, RequestLogList
from typing import Optional
from datetime import datetime
from uuid import UUID

router = APIRouter()


@router.get("", response_model=RequestLogList)
async def get_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    provider: Optional[str] = None,
    model: Optional[str] = None,
    status_code: Optional[int] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取请求日志列表"""
    query = select(RequestLog)
    count_query = select(func.count()).select_from(RequestLog)
    
    # 构建筛选条件
    conditions = []
    
    if provider:
        conditions.append(RequestLog.provider == provider)
    
    if model:
        conditions.append(RequestLog.model == model)
    
    if status_code is not None:
        conditions.append(RequestLog.status_code == status_code)
    
    if start_time:
        conditions.append(RequestLog.created_at >= start_time)
    
    if end_time:
        conditions.append(RequestLog.created_at <= end_time)
    
    if search:
        # 搜索请求ID、供应商请求ID、错误信息、用户输入文本、AI返回文本等
        search_condition = or_(
            RequestLog.request_id.ilike(f"%{search}%"),
            RequestLog.provider_request_id.ilike(f"%{search}%"),
            RequestLog.error_message.ilike(f"%{search}%"),
            RequestLog.user_id.ilike(f"%{search}%"),
            RequestLog.user_input_text.ilike(f"%{search}%"),
            RequestLog.ai_response_text.ilike(f"%{search}%")
        )
        conditions.append(search_condition)
    
    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))
    
    # 获取总数
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # 分页和排序
    query = query.order_by(RequestLog.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    # 执行查询
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return RequestLogList(
        total=total,
        page=page,
        page_size=page_size,
        items=[RequestLogResponse.model_validate(log) for log in logs]
    )


@router.get("/{log_id}", response_model=RequestLogResponse)
async def get_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """获取单个日志详情"""
    result = await db.execute(
        select(RequestLog).where(RequestLog.id == log_id)
    )
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    return RequestLogResponse.model_validate(log)


@router.delete("/{log_id}")
async def delete_log(
    log_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """删除日志"""
    result = await db.execute(
        select(RequestLog).where(RequestLog.id == log_id)
    )
    log = result.scalar_one_or_none()
    
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    await db.delete(log)
    await db.commit()
    
    return {"message": "Log deleted successfully"}


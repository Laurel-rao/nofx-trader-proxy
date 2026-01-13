from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, case
from app.database import get_db
from app.models.request_log import RequestLog
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()


class StatsSummary(BaseModel):
    total_requests: int
    total_tokens: int
    total_prompt_tokens: int
    total_completion_tokens: int
    avg_duration_ms: float
    success_count: int
    error_count: int
    total_cost: float
    avg_cost: float


class TimelineStats(BaseModel):
    time: str
    requests: int
    tokens: int
    avg_duration_ms: float
    cost: float


class ModelStats(BaseModel):
    model: str
    requests: int
    tokens: int
    avg_duration_ms: float
    cost: float


class ProviderCostStats(BaseModel):
    provider: str
    requests: int
    cost: float
    avg_cost: float


@router.get("/summary", response_model=StatsSummary)
async def get_summary(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取统计摘要"""
    query = select(
        func.count(RequestLog.id).label("total_requests"),
        func.coalesce(func.sum(RequestLog.total_tokens), 0).label("total_tokens"),
        func.coalesce(func.sum(RequestLog.prompt_tokens), 0).label("total_prompt_tokens"),
        func.coalesce(func.sum(RequestLog.completion_tokens), 0).label("total_completion_tokens"),
        func.avg(RequestLog.duration_ms).label("avg_duration_ms"),
        func.sum(
            case(
                (RequestLog.status_code == 200, 1),
                else_=0
            )
        ).label("success_count"),
        func.sum(
            case(
                (RequestLog.status_code != 200, 1),
                else_=0
            )
        ).label("error_count"),
        func.coalesce(func.sum(RequestLog.actual_cost), 0).label("total_cost"),
        func.avg(RequestLog.actual_cost).label("avg_cost")
    )
    
    conditions = []
    if start_time:
        conditions.append(RequestLog.created_at >= start_time)
    if end_time:
        conditions.append(RequestLog.created_at <= end_time)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    result = await db.execute(query)
    row = result.first()
    
    return StatsSummary(
        total_requests=row.total_requests or 0,
        total_tokens=row.total_tokens or 0,
        total_prompt_tokens=row.total_prompt_tokens or 0,
        total_completion_tokens=row.total_completion_tokens or 0,
        avg_duration_ms=float(row.avg_duration_ms or 0),
        success_count=row.success_count or 0,
        error_count=row.error_count or 0,
        total_cost=float(row.total_cost or 0),
        avg_cost=float(row.avg_cost or 0)
    )


@router.get("/timeline", response_model=List[TimelineStats])
async def get_timeline(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    group_by: str = Query("hour", regex="^(hour|day)$"),
    db: AsyncSession = Depends(get_db)
):
    """获取时间线统计"""
    # 默认查询最近7天
    if not end_time:
        end_time = datetime.utcnow()
    if not start_time:
        start_time = end_time - timedelta(days=7)
    
    # 根据分组类型选择时间格式
    if group_by == "hour":
        time_format = func.to_char(RequestLog.created_at, "YYYY-MM-DD HH24:00:00")
    else:  # day
        time_format = func.to_char(RequestLog.created_at, "YYYY-MM-DD")
    
    query = select(
        time_format.label("time"),
        func.count(RequestLog.id).label("requests"),
        func.coalesce(func.sum(RequestLog.total_tokens), 0).label("tokens"),
        func.avg(RequestLog.duration_ms).label("avg_duration_ms"),
        func.coalesce(func.sum(RequestLog.actual_cost), 0).label("cost")
    ).where(
        and_(
            RequestLog.created_at >= start_time,
            RequestLog.created_at <= end_time
        )
    ).group_by("time").order_by("time")
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        TimelineStats(
            time=row.time,
            requests=row.requests,
            tokens=row.tokens or 0,
            avg_duration_ms=float(row.avg_duration_ms or 0),
            cost=float(row.cost or 0)
        )
        for row in rows
    ]


@router.get("/tokens", response_model=dict)
async def get_token_stats(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """获取 Token 使用统计"""
    conditions = []
    if start_time:
        conditions.append(RequestLog.created_at >= start_time)
    if end_time:
        conditions.append(RequestLog.created_at <= end_time)
    
    query = select(
        func.sum(RequestLog.prompt_tokens).label("total_prompt"),
        func.sum(RequestLog.completion_tokens).label("total_completion"),
        func.sum(RequestLog.total_tokens).label("total"),
        func.avg(RequestLog.prompt_tokens).label("avg_prompt"),
        func.avg(RequestLog.completion_tokens).label("avg_completion")
    )
    
    if conditions:
        query = query.where(and_(*conditions))
    
    result = await db.execute(query)
    row = result.first()
    
    return {
        "total_prompt_tokens": row.total_prompt or 0,
        "total_completion_tokens": row.total_completion or 0,
        "total_tokens": row.total or 0,
        "avg_prompt_tokens": float(row.avg_prompt or 0),
        "avg_completion_tokens": float(row.avg_completion or 0)
    }


@router.get("/models", response_model=List[ModelStats])
async def get_model_stats(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """按模型统计使用情况"""
    conditions = []
    if start_time:
        conditions.append(RequestLog.created_at >= start_time)
    if end_time:
        conditions.append(RequestLog.created_at <= end_time)
    
    query = select(
        RequestLog.model,
        func.count(RequestLog.id).label("requests"),
        func.coalesce(func.sum(RequestLog.total_tokens), 0).label("tokens"),
        func.avg(RequestLog.duration_ms).label("avg_duration_ms"),
        func.coalesce(func.sum(RequestLog.actual_cost), 0).label("cost")
    ).group_by(RequestLog.model)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(func.count(RequestLog.id).desc())
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        ModelStats(
            model=row.model,
            requests=row.requests,
            tokens=row.tokens or 0,
            avg_duration_ms=float(row.avg_duration_ms or 0),
            cost=float(row.cost or 0)
        )
        for row in rows
    ]


@router.get("/costs", response_model=List[ProviderCostStats])
async def get_provider_cost_stats(
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """按供应商统计费用"""
    conditions = []
    if start_time:
        conditions.append(RequestLog.created_at >= start_time)
    if end_time:
        conditions.append(RequestLog.created_at <= end_time)
    
    query = select(
        RequestLog.provider,
        func.count(RequestLog.id).label("requests"),
        func.coalesce(func.sum(RequestLog.actual_cost), 0).label("cost"),
        func.avg(RequestLog.actual_cost).label("avg_cost")
    ).group_by(RequestLog.provider)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(func.sum(RequestLog.actual_cost).desc())
    
    result = await db.execute(query)
    rows = result.all()
    
    return [
        ProviderCostStats(
            provider=row.provider,
            requests=row.requests,
            cost=float(row.cost or 0),
            avg_cost=float(row.avg_cost or 0)
        )
        for row in rows
    ]


"""
供应商统计信息服务
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case, and_
from app.models.request_log import RequestLog
from typing import Dict, Optional
from datetime import datetime


async def get_provider_statistics(
    db: AsyncSession,
    provider_name: str
) -> Dict:
    """
    获取供应商的统计信息
    
    Returns:
        dict: 包含访问次数、计费总额、成功/失败次数、成功率、最近访问时间
    """
    # 构建查询条件
    conditions = [RequestLog.provider == provider_name]
    
    # 统计查询
    query = select(
        func.count(RequestLog.id).label("total_requests"),
        func.coalesce(func.sum(RequestLog.actual_cost), 0).label("total_cost"),
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
        ).label("failure_count"),
        func.max(RequestLog.created_at).label("last_access_time")
    ).where(and_(*conditions))
    
    result = await db.execute(query)
    row = result.first()
    
    total_requests = row.total_requests or 0
    total_cost = float(row.total_cost or 0)
    success_count = row.success_count or 0
    failure_count = row.failure_count or 0
    last_access_time = row.last_access_time
    
    # 计算成功率
    success_rate = 0.0
    if total_requests > 0:
        success_rate = round((success_count / total_requests) * 100, 2)
    
    return {
        "total_requests": total_requests,
        "total_cost": total_cost,
        "success_count": success_count,
        "failure_count": failure_count,
        "success_rate": success_rate,
        "last_access_time": last_access_time.isoformat() if last_access_time else None
    }


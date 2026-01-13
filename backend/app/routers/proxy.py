from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.proxy_service import proxy_request
from app.services.logger_service import create_request_log
from typing import Dict, Any, Optional
import json
import traceback
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/chat/completions")
async def chat_completions(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    代理 OpenAI Chat Completions API
    接收标准 OpenAI 格式的请求，转发到配置的模型供应商
    
    Authorization Header 格式：
    - Bearer <供应商名称> - 指定使用哪个供应商
    - 如果不提供或格式不正确，则使用默认的活跃供应商
    """
    try:
        # 获取请求体
        request_data = await request.json()
        
        # 从请求头获取用户标识（可选）
        user_id = request.headers.get("X-User-ID")
        
        # 获取客户端 IP 地址
        client_ip = request.client.host if request.client else None
        # 如果通过代理，尝试从 X-Forwarded-For 或 X-Real-IP 获取真实 IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            real_ip = request.headers.get("X-Real-IP")
            if real_ip:
                client_ip = real_ip
        
        # 从 Authorization header 中提取供应商名称
        provider_name = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            provider_name = auth_header.replace("Bearer ", "").strip()
            # 如果为空，则使用 None（将使用默认供应商）
            if not provider_name:
                provider_name = None
        
        # 代理请求
        response_data, status_code, error_message, log_data = await proxy_request(
            db=db,
            request_data=request_data,
            user_id=user_id,
            provider_name=provider_name,
            client_ip=client_ip
        )
        
        # 在后台任务中记录日志
        background_tasks.add_task(create_request_log, db, log_data)
        
        # 返回响应
        if status_code == 200:
            return JSONResponse(content=response_data, status_code=status_code)
        else:
            return JSONResponse(
                content=response_data,
                status_code=status_code
            )
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        # 打印完整的 traceback
        logger.error(f"Error in chat_completions: {str(e)}")
        logger.error(traceback.format_exc())
        print(f"\n{'='*60}")
        print("ERROR TRACEBACK:")
        print('='*60)
        traceback.print_exc()
        print('='*60 + "\n")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


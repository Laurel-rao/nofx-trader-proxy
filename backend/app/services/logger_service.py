from sqlalchemy.ext.asyncio import AsyncSession
from app.models.request_log import RequestLog
from app.schemas.request_log import RequestLogCreate
from app.services.billing_service import calculate_cost
from typing import Optional, Dict, Any
from decimal import Decimal
import uuid
import json


async def create_request_log(db: AsyncSession, log_data: RequestLogCreate) -> RequestLog:
    """创建请求日志"""
    # 解析请求和响应的详细信息
    request_details = parse_request_details(log_data.request_params)
    response_details = parse_response_details(log_data.response_content)
    
    db_log = RequestLog(
        request_id=log_data.request_id,
        provider=log_data.provider,
        model=log_data.model,
        request_params=log_data.request_params,
        response_content=log_data.response_content,
        prompt_tokens=log_data.prompt_tokens,
        completion_tokens=log_data.completion_tokens,
        total_tokens=log_data.total_tokens,
        duration_ms=log_data.duration_ms,
        status_code=log_data.status_code,
        error_message=log_data.error_message,
        user_id=log_data.user_id,
        provider_request_id=log_data.provider_request_id,
        client_ip=log_data.client_ip,
        # 解析后的详细字段
        user_input_text=request_details.get("user_input_text"),
        ai_response_text=response_details.get("ai_response_text"),
        temperature=request_details.get("temperature"),
        top_p=request_details.get("top_p"),
        top_k=request_details.get("top_k"),
        max_tokens=request_details.get("max_tokens"),
        frequency_penalty=request_details.get("frequency_penalty"),
        presence_penalty=request_details.get("presence_penalty"),
        stream=request_details.get("stream"),
        # 计费相关字段
        user_discount_rate=Decimal(str(log_data.user_discount_rate)) if log_data.user_discount_rate is not None else None,
        actual_cost=Decimal(str(log_data.actual_cost)) if log_data.actual_cost is not None else None,
        model_rate=Decimal(str(log_data.model_rate)) if log_data.model_rate is not None else None,
        completion_rate=Decimal(str(log_data.completion_rate)) if log_data.completion_rate is not None else None,
        group_rate=Decimal(str(log_data.group_rate)) if log_data.group_rate is not None else None,
        recharge_rate=Decimal(str(log_data.recharge_rate)) if log_data.recharge_rate is not None else None
    )
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log


def extract_tokens_from_response(response_data: Dict[str, Any]) -> tuple[int, int, int]:
    """从 OpenAI 响应中提取 token 使用量"""
    usage = response_data.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)
    return prompt_tokens, completion_tokens, total_tokens


def parse_request_details(request_params: Dict[str, Any]) -> Dict[str, Any]:
    """解析请求参数，提取详细信息"""
    details = {}
    
    # 提取用户输入文本
    messages = request_params.get("messages", [])
    user_messages = [msg.get("content", "") for msg in messages if msg.get("role") == "user"]
    details["user_input_text"] = "\n".join(user_messages) if user_messages else None
    
    # 提取参数
    details["temperature"] = str(request_params.get("temperature")) if request_params.get("temperature") is not None else None
    details["top_p"] = str(request_params.get("top_p")) if request_params.get("top_p") is not None else None
    details["top_k"] = str(request_params.get("top_k")) if request_params.get("top_k") is not None else None
    details["max_tokens"] = request_params.get("max_tokens")
    details["frequency_penalty"] = str(request_params.get("frequency_penalty")) if request_params.get("frequency_penalty") is not None else None
    details["presence_penalty"] = str(request_params.get("presence_penalty")) if request_params.get("presence_penalty") is not None else None
    details["stream"] = str(request_params.get("stream", False)).lower()
    
    return details


def parse_response_details(response_content: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """解析响应内容，提取AI返回的文本"""
    details = {}
    
    if not response_content:
        details["ai_response_text"] = None
        return details
    
    # 提取AI返回的文本
    choices = response_content.get("choices", [])
    if choices:
        messages = []
        for choice in choices:
            message = choice.get("message", {})
            content = message.get("content", "")
            if content:
                messages.append(content)
        details["ai_response_text"] = "\n".join(messages) if messages else None
    else:
        details["ai_response_text"] = None
    
    return details


def generate_request_id() -> str:
    """生成请求唯一标识"""
    return str(uuid.uuid4())


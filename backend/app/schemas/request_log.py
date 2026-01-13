from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class RequestLogCreate(BaseModel):
    request_id: str
    provider: str
    model: str
    request_params: Dict[str, Any]
    response_content: Optional[Dict[str, Any]] = None
    prompt_tokens: Optional[int] = 0
    completion_tokens: Optional[int] = 0
    total_tokens: Optional[int] = 0
    duration_ms: int
    status_code: int = 200
    error_message: Optional[str] = None
    user_id: Optional[str] = None
    provider_request_id: Optional[str] = None  # 供应商返回的 request id
    client_ip: Optional[str] = None  # 客户端 IP 地址
    # 解析后的详细字段
    user_input_text: Optional[str] = None
    ai_response_text: Optional[str] = None
    temperature: Optional[str] = None
    top_p: Optional[str] = None
    top_k: Optional[str] = None
    max_tokens: Optional[int] = None
    frequency_penalty: Optional[str] = None
    presence_penalty: Optional[str] = None
    stream: Optional[str] = None
    # 计费相关字段
    user_discount_rate: Optional[float] = None
    actual_cost: Optional[float] = None
    model_rate: Optional[float] = None
    completion_rate: Optional[float] = None
    group_rate: Optional[float] = None
    recharge_rate: Optional[float] = None


class RequestLogResponse(BaseModel):
    id: UUID
    created_at: datetime
    request_id: str
    provider: str
    model: str
    request_params: Dict[str, Any]
    response_content: Optional[Dict[str, Any]] = None
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    total_tokens: Optional[int]
    duration_ms: int
    status_code: int
    error_message: Optional[str]
    user_id: Optional[str]
    provider_request_id: Optional[str] = None  # 供应商返回的 request id
    client_ip: Optional[str] = None  # 客户端 IP 地址
    # 解析后的详细字段
    user_input_text: Optional[str] = None
    ai_response_text: Optional[str] = None
    temperature: Optional[str] = None
    top_p: Optional[str] = None
    top_k: Optional[str] = None
    max_tokens: Optional[int] = None
    frequency_penalty: Optional[str] = None
    presence_penalty: Optional[str] = None
    stream: Optional[str] = None
    # 计费相关字段
    user_discount_rate: Optional[float] = None
    actual_cost: Optional[float] = None
    model_rate: Optional[float] = None
    completion_rate: Optional[float] = None
    group_rate: Optional[float] = None
    recharge_rate: Optional[float] = None

    class Config:
        from_attributes = True


class RequestLogList(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[RequestLogResponse]


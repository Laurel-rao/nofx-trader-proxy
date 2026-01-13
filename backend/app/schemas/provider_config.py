from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class ProviderConfigCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    api_base_url: str = Field(..., min_length=1)
    api_key: str = Field(..., min_length=1)
    default_model: str = Field(..., min_length=1, max_length=100)
    is_enabled: bool = True
    priority: int = Field(default=0, ge=0)
    # 计费配置
    model_rate: Optional[float] = Field(default=1.0, ge=0, description="模型倍率")
    completion_rate: Optional[float] = Field(default=1.0, ge=0, description="补全倍率")
    group_rate: Optional[float] = Field(default=1.0, ge=0, description="分组倍率")
    recharge_rate: Optional[float] = Field(default=1.0, ge=0, description="充值转换率")


class ProviderConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_base_url: Optional[str] = Field(None, min_length=1)
    api_key: Optional[str] = Field(None, min_length=1)
    default_model: Optional[str] = Field(None, min_length=1, max_length=100)
    is_enabled: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0)
    # 计费配置
    model_rate: Optional[float] = Field(None, ge=0, description="模型倍率")
    completion_rate: Optional[float] = Field(None, ge=0, description="补全倍率")
    group_rate: Optional[float] = Field(None, ge=0, description="分组倍率")
    recharge_rate: Optional[float] = Field(None, ge=0, description="充值转换率")


class ProviderConfigResponse(BaseModel):
    id: UUID
    name: str
    api_base_url: str
    api_key: str  # 返回时显示加密后的值或部分隐藏
    default_model: str
    is_enabled: bool
    priority: int
    created_at: datetime
    updated_at: datetime
    # 计费配置
    model_rate: Optional[float] = None
    completion_rate: Optional[float] = None
    group_rate: Optional[float] = None
    recharge_rate: Optional[float] = None
    # 统计信息（可选，仅在列表接口中返回）
    statistics: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


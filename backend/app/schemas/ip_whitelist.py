from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class IPWhitelistCreate(BaseModel):
    ip_address: str = Field(..., description="IP地址或CIDR格式（如 192.168.1.0/24）")
    description: Optional[str] = Field(None, description="描述信息")
    is_global: bool = Field(False, description="是否为全局白名单")
    provider_id: Optional[UUID] = Field(None, description="关联的供应商ID（供应商白名单时必填）")
    is_enabled: bool = Field(True, description="是否启用")


class IPWhitelistUpdate(BaseModel):
    ip_address: Optional[str] = None
    description: Optional[str] = None
    is_enabled: Optional[bool] = None


class IPWhitelistResponse(BaseModel):
    id: UUID
    ip_address: str
    description: Optional[str]
    is_global: bool
    provider_id: Optional[UUID]
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
    provider_name: Optional[str] = None  # 供应商名称（用于显示）

    class Config:
        from_attributes = True


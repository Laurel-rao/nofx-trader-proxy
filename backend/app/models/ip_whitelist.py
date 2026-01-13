from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class IPWhitelist(Base):
    __tablename__ = "ip_whitelists"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ip_address = Column(String(50), nullable=False, index=True)  # IP地址或CIDR格式
    description = Column(String(255), nullable=True)  # 描述信息
    is_global = Column(Boolean, nullable=False, default=False, index=True)  # 是否为全局白名单
    provider_id = Column(UUID(as_uuid=True), ForeignKey("provider_configs.id", ondelete="CASCADE"), nullable=True, index=True)  # 关联的供应商ID（如果为None且is_global=False，则为全局）
    is_enabled = Column(Boolean, nullable=False, default=True, index=True)  # 是否启用
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 关联关系
    provider = relationship("ProviderConfig", backref="ip_whitelists")


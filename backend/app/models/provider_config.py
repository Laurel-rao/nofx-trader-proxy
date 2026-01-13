from sqlalchemy import Column, String, Boolean, Integer, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.database import Base


class ProviderConfig(Base):
    __tablename__ = "provider_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    api_base_url = Column(String(500), nullable=False)
    api_key = Column(String(500), nullable=False)  # 加密存储
    default_model = Column(String(100), nullable=False)
    is_enabled = Column(Boolean, nullable=False, default=True, index=True)
    priority = Column(Integer, nullable=False, default=0, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 计费配置
    model_rate = Column(Numeric(10, 4), nullable=True, default=1.0)  # 模型倍率
    completion_rate = Column(Numeric(10, 4), nullable=True, default=1.0)  # 补全倍率
    group_rate = Column(Numeric(10, 4), nullable=True, default=1.0)  # 分组倍率
    recharge_rate = Column(Numeric(10, 4), nullable=True, default=1.0)  # 充值转换率


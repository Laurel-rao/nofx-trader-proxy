from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from app.database import Base


class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    request_id = Column(String(255), unique=True, nullable=False, index=True)
    provider = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    request_params = Column(JSONB, nullable=False)
    response_content = Column(JSONB, nullable=True)
    prompt_tokens = Column(Integer, nullable=True, default=0)
    completion_tokens = Column(Integer, nullable=True, default=0)
    total_tokens = Column(Integer, nullable=True, default=0)
    duration_ms = Column(Integer, nullable=False, default=0)
    status_code = Column(Integer, nullable=False, default=200)
    error_message = Column(Text, nullable=True)
    user_id = Column(String(255), nullable=True, index=True)
    provider_request_id = Column(String(255), nullable=True, index=True)  # 供应商返回的 request id
    client_ip = Column(String(50), nullable=True, index=True)  # 客户端 IP 地址
    
    # 解析后的详细字段
    user_input_text = Column(Text, nullable=True)  # 用户输入的文本内容
    ai_response_text = Column(Text, nullable=True)  # AI返回的文本内容
    temperature = Column(String(50), nullable=True)  # 温度参数
    top_p = Column(String(50), nullable=True)  # Top P 参数
    top_k = Column(String(50), nullable=True)  # Top K 参数
    max_tokens = Column(Integer, nullable=True)  # 最大token数
    frequency_penalty = Column(String(50), nullable=True)  # 频率惩罚
    presence_penalty = Column(String(50), nullable=True)  # 存在惩罚
    stream = Column(String(10), nullable=True)  # 是否流式
    
    # 计费相关字段
    user_discount_rate = Column(Numeric(10, 4), nullable=True, default=1.0)  # 用户折扣率
    actual_cost = Column(Numeric(20, 6), nullable=True)  # 实际扣费（美元）
    model_rate = Column(Numeric(10, 4), nullable=True)  # 使用的模型倍率
    completion_rate = Column(Numeric(10, 4), nullable=True)  # 使用的补全倍率
    group_rate = Column(Numeric(10, 4), nullable=True)  # 使用的分组倍率
    recharge_rate = Column(Numeric(10, 4), nullable=True)  # 使用的充值转换率


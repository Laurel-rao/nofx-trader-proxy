"""
计费计算服务
根据公式计算实际扣费：
(输入tokens + 输出tokens × 补全倍率) × 模型倍率 × 分组倍率 × 充值转换率 × 用户折扣率 / 500000
"""
from typing import Optional
from decimal import Decimal
from app.models.provider_config import ProviderConfig


def calculate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    provider: ProviderConfig,
    user_discount_rate: Optional[Decimal] = None
) -> dict:
    """
    计算实际扣费
    
    Args:
        prompt_tokens: 输入tokens
        completion_tokens: 输出tokens
        provider: 供应商配置
        user_discount_rate: 用户折扣率（可选，默认为1.0）
    
    Returns:
        dict: 包含计费详情的字典
    """
    # 获取倍率配置，如果为None则使用默认值
    model_rate = Decimal(str(provider.model_rate)) if provider.model_rate is not None else Decimal('1.0')
    completion_rate = Decimal(str(provider.completion_rate)) if provider.completion_rate is not None else Decimal('1.0')
    group_rate = Decimal(str(provider.group_rate)) if provider.group_rate is not None else Decimal('1.0')
    recharge_rate = Decimal(str(provider.recharge_rate)) if provider.recharge_rate is not None else Decimal('1.0')
    discount_rate = Decimal(str(user_discount_rate)) if user_discount_rate is not None else Decimal('1.0')
    
    # 转换为Decimal确保精度
    prompt_tokens_decimal = Decimal(str(prompt_tokens))
    completion_tokens_decimal = Decimal(str(completion_tokens))
    
    # 计算过程
    # (输入tokens + 输出tokens × 补全倍率) × 模型倍率 × 分组倍率 × 充值转换率 × 用户折扣率 / 500000
    base_tokens = prompt_tokens_decimal + completion_tokens_decimal * completion_rate
    cost = base_tokens * model_rate * group_rate * recharge_rate * discount_rate / Decimal('500000')
    
    return {
        "actual_cost": float(cost),
        "model_rate": float(model_rate),
        "completion_rate": float(completion_rate),
        "group_rate": float(group_rate),
        "recharge_rate": float(recharge_rate),
        "user_discount_rate": float(discount_rate),
        "base_tokens": float(base_tokens),
        "calculation_formula": f"({prompt_tokens} + {completion_tokens} × {completion_rate}) × {model_rate} × {group_rate} × {recharge_rate} × {discount_rate} / 500000"
    }


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.provider_config import ProviderConfig
from app.schemas.provider_config import ProviderConfigCreate, ProviderConfigUpdate
from app.services.encryption import encrypt_api_key, decrypt_api_key
from typing import Optional
import uuid


async def get_provider_configs(db: AsyncSession, enabled_only: bool = False) -> list[ProviderConfig]:
    """获取供应商配置列表"""
    query = select(ProviderConfig)
    if enabled_only:
        query = query.where(ProviderConfig.is_enabled == True)
    query = query.order_by(ProviderConfig.priority.asc(), ProviderConfig.created_at.asc())
    result = await db.execute(query)
    return result.scalars().all()


async def get_provider_config(db: AsyncSession, provider_id: uuid.UUID) -> Optional[ProviderConfig]:
    """根据 ID 获取供应商配置"""
    result = await db.execute(select(ProviderConfig).where(ProviderConfig.id == provider_id))
    return result.scalar_one_or_none()


async def get_provider_by_name(db: AsyncSession, name: str) -> Optional[ProviderConfig]:
    """根据名称获取供应商配置"""
    result = await db.execute(select(ProviderConfig).where(ProviderConfig.name == name))
    return result.scalar_one_or_none()


async def get_active_provider(db: AsyncSession) -> Optional[ProviderConfig]:
    """获取优先级最高的启用供应商"""
    result = await db.execute(
        select(ProviderConfig)
        .where(ProviderConfig.is_enabled == True)
        .order_by(ProviderConfig.priority.asc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def create_provider_config(db: AsyncSession, config: ProviderConfigCreate) -> ProviderConfig:
    """创建供应商配置"""
    # 加密 API Key
    encrypted_key = encrypt_api_key(config.api_key)
    
    db_config = ProviderConfig(
        name=config.name,
        api_base_url=config.api_base_url,
        api_key=encrypted_key,
        default_model=config.default_model,
        is_enabled=config.is_enabled,
        priority=config.priority,
        model_rate=config.model_rate,
        completion_rate=config.completion_rate,
        group_rate=config.group_rate,
        recharge_rate=config.recharge_rate
    )
    db.add(db_config)
    await db.commit()
    await db.refresh(db_config)
    return db_config


async def update_provider_config(
    db: AsyncSession,
    provider_id: uuid.UUID,
    config: ProviderConfigUpdate
) -> Optional[ProviderConfig]:
    """更新供应商配置"""
    db_config = await get_provider_config(db, provider_id)
    if not db_config:
        return None
    
    update_data = config.model_dump(exclude_unset=True)
    
    # 如果更新了 API Key，需要加密
    # 如果 API Key 为空字符串，则不更新（保留原有值）
    if "api_key" in update_data:
        if update_data["api_key"] and update_data["api_key"].strip():
            update_data["api_key"] = encrypt_api_key(update_data["api_key"])
        else:
            # 如果 API Key 为空，移除该字段，保留原有值
            del update_data["api_key"]
    
    for key, value in update_data.items():
        # 处理计费字段，转换为Decimal
        if key in ['model_rate', 'completion_rate', 'group_rate', 'recharge_rate'] and value is not None:
            from decimal import Decimal
            setattr(db_config, key, Decimal(str(value)))
        else:
            setattr(db_config, key, value)
    
    await db.commit()
    await db.refresh(db_config)
    return db_config


async def delete_provider_config(db: AsyncSession, provider_id: uuid.UUID) -> bool:
    """删除供应商配置"""
    db_config = await get_provider_config(db, provider_id)
    if not db_config:
        return False
    
    await db.delete(db_config)
    await db.commit()
    return True


async def toggle_provider_config(db: AsyncSession, provider_id: uuid.UUID) -> Optional[ProviderConfig]:
    """切换供应商启用状态"""
    db_config = await get_provider_config(db, provider_id)
    if not db_config:
        return None
    
    db_config.is_enabled = not db_config.is_enabled
    await db.commit()
    await db.refresh(db_config)
    return db_config


def get_decrypted_api_key(provider: ProviderConfig) -> str:
    """获取解密后的 API Key"""
    return decrypt_api_key(provider.api_key)


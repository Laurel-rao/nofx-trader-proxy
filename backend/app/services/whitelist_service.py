"""
IP白名单服务
支持全局白名单和供应商级别的白名单
"""
import ipaddress
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.models.ip_whitelist import IPWhitelist
from uuid import UUID


def is_ip_in_network(ip: str, network: str) -> bool:
    """
    检查IP是否在指定的网络范围内（支持CIDR格式）
    
    Args:
        ip: 要检查的IP地址
        network: IP地址或CIDR格式的网络（如 192.168.1.0/24）
    
    Returns:
        bool: IP是否在网络范围内
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        network_obj = ipaddress.ip_network(network, strict=False)
        return ip_obj in network_obj
    except (ValueError, ipaddress.AddressValueError):
        return False


async def check_ip_whitelist(
    db: AsyncSession,
    client_ip: Optional[str],
    provider_id: Optional[UUID] = None
) -> tuple[bool, Optional[str]]:
    """
    检查IP是否在白名单中
    
    Args:
        db: 数据库会话
        client_ip: 客户端IP地址
        provider_id: 供应商ID（可选，如果提供则检查供应商级别的白名单）
    
    Returns:
        tuple[bool, Optional[str]]: (是否允许访问, 错误信息)
    """
    if not client_ip:
        return False, "无法获取客户端IP地址"
    
    # 查询全局白名单
    global_query = select(IPWhitelist).where(
        IPWhitelist.is_global == True,
        IPWhitelist.is_enabled == True
    )
    global_result = await db.execute(global_query)
    global_whitelists = global_result.scalars().all()
    
    # 检查全局白名单
    for whitelist in global_whitelists:
        if is_ip_in_network(client_ip, whitelist.ip_address):
            return True, None
    
    # 如果指定了供应商，检查供应商级别的白名单
    if provider_id:
        provider_query = select(IPWhitelist).where(
            IPWhitelist.provider_id == provider_id,
            IPWhitelist.is_enabled == True
        )
        provider_result = await db.execute(provider_query)
        provider_whitelists = provider_result.scalars().all()
        
        for whitelist in provider_whitelists:
            if is_ip_in_network(client_ip, whitelist.ip_address):
                return True, None
    
    # 如果没有任何白名单规则，默认允许访问（可以根据需求修改）
    # 这里我们检查是否有任何白名单规则存在
    all_query = select(IPWhitelist).where(IPWhitelist.is_enabled == True)
    all_result = await db.execute(all_query)
    all_whitelists = all_result.scalars().all()
    
    # 如果存在白名单规则但IP不在其中，则拒绝访问
    if all_whitelists:
        return False, f"IP地址 {client_ip} 不在白名单中"
    
    # 如果没有任何白名单规则，默认允许访问
    return True, None


async def get_whitelists(
    db: AsyncSession,
    provider_id: Optional[UUID] = None,
    is_global: Optional[bool] = None
) -> List[IPWhitelist]:
    """获取白名单列表"""
    query = select(IPWhitelist)
    
    conditions = []
    if provider_id is not None:
        conditions.append(IPWhitelist.provider_id == provider_id)
    if is_global is not None:
        conditions.append(IPWhitelist.is_global == is_global)
    
    if conditions:
        query = query.where(or_(*conditions))
    
    query = query.order_by(IPWhitelist.is_global.desc(), IPWhitelist.created_at.desc())
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_whitelist(
    db: AsyncSession,
    ip_address: str,
    description: Optional[str] = None,
    is_global: bool = False,
    provider_id: Optional[UUID] = None,
    is_enabled: bool = True
) -> IPWhitelist:
    """创建白名单规则"""
    # 验证IP地址格式
    try:
        if '/' in ip_address:
            ipaddress.ip_network(ip_address, strict=False)
        else:
            ipaddress.ip_address(ip_address)
    except (ValueError, ipaddress.AddressValueError):
        raise ValueError(f"无效的IP地址格式: {ip_address}")
    
    # 验证逻辑：全局白名单不能关联供应商
    if is_global and provider_id:
        raise ValueError("全局白名单不能关联供应商")
    
    # 验证逻辑：非全局白名单必须关联供应商
    if not is_global and not provider_id:
        raise ValueError("供应商白名单必须关联供应商")
    
    whitelist = IPWhitelist(
        ip_address=ip_address,
        description=description,
        is_global=is_global,
        provider_id=provider_id,
        is_enabled=is_enabled
    )
    
    db.add(whitelist)
    await db.commit()
    await db.refresh(whitelist)
    return whitelist


async def delete_whitelist(db: AsyncSession, whitelist_id: UUID) -> bool:
    """删除白名单规则"""
    result = await db.execute(
        select(IPWhitelist).where(IPWhitelist.id == whitelist_id)
    )
    whitelist = result.scalar_one_or_none()
    
    if not whitelist:
        return False
    
    await db.delete(whitelist)
    await db.commit()
    return True


async def toggle_whitelist(db: AsyncSession, whitelist_id: UUID) -> Optional[IPWhitelist]:
    """切换白名单规则启用状态"""
    result = await db.execute(
        select(IPWhitelist).where(IPWhitelist.id == whitelist_id)
    )
    whitelist = result.scalar_one_or_none()
    
    if not whitelist:
        return None
    
    whitelist.is_enabled = not whitelist.is_enabled
    await db.commit()
    await db.refresh(whitelist)
    return whitelist


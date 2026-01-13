from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.whitelist_service import (
    get_whitelists,
    create_whitelist,
    delete_whitelist,
    toggle_whitelist
)
from app.schemas.ip_whitelist import (
    IPWhitelistCreate,
    IPWhitelistUpdate,
    IPWhitelistResponse
)
from uuid import UUID
from typing import List, Optional

router = APIRouter()


@router.get("", response_model=List[IPWhitelistResponse])
async def list_whitelists(
    provider_id: Optional[UUID] = Query(None, description="供应商ID"),
    is_global: Optional[bool] = Query(None, description="是否为全局白名单"),
    db: AsyncSession = Depends(get_db)
):
    """获取白名单列表"""
    whitelists = await get_whitelists(db, provider_id=provider_id, is_global=is_global)
    
    result = []
    for whitelist in whitelists:
        whitelist_dict = IPWhitelistResponse.model_validate(whitelist).model_dump()
        if whitelist.provider:
            whitelist_dict["provider_name"] = whitelist.provider.name
        result.append(IPWhitelistResponse(**whitelist_dict))
    
    return result


@router.post("", response_model=IPWhitelistResponse, status_code=201)
async def create_whitelist_rule(
    whitelist: IPWhitelistCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建白名单规则"""
    try:
        created = await create_whitelist(
            db=db,
            ip_address=whitelist.ip_address,
            description=whitelist.description,
            is_global=whitelist.is_global,
            provider_id=whitelist.provider_id,
            is_enabled=whitelist.is_enabled
        )
        
        whitelist_dict = IPWhitelistResponse.model_validate(created).model_dump()
        if created.provider:
            whitelist_dict["provider_name"] = created.provider.name
        
        return IPWhitelistResponse(**whitelist_dict)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{whitelist_id}")
async def delete_whitelist_rule(
    whitelist_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """删除白名单规则"""
    success = await delete_whitelist(db, whitelist_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Whitelist not found")
    
    return {"message": "Whitelist deleted successfully"}


@router.put("/{whitelist_id}/toggle", response_model=IPWhitelistResponse)
async def toggle_whitelist_rule(
    whitelist_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """切换白名单规则启用状态"""
    whitelist = await toggle_whitelist(db, whitelist_id)
    
    if not whitelist:
        raise HTTPException(status_code=404, detail="Whitelist not found")
    
    whitelist_dict = IPWhitelistResponse.model_validate(whitelist).model_dump()
    if whitelist.provider:
        whitelist_dict["provider_name"] = whitelist.provider.name
    
    return IPWhitelistResponse(**whitelist_dict)


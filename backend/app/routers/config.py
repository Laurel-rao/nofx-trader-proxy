from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.provider_service import (
    get_provider_configs,
    get_provider_config,
    create_provider_config,
    update_provider_config,
    delete_provider_config,
    toggle_provider_config
)
from app.schemas.provider_config import (
    ProviderConfigCreate,
    ProviderConfigUpdate,
    ProviderConfigResponse
)
from app.services.encryption import mask_api_key
from app.services.provider_stats_service import get_provider_statistics
from uuid import UUID
from typing import List
from pydantic import BaseModel
import httpx
import os
from pathlib import Path

router = APIRouter()


@router.get("/providers", response_model=List[ProviderConfigResponse])
async def list_providers(
    enabled_only: bool = False,
    include_stats: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """获取供应商配置列表"""
    providers = await get_provider_configs(db, enabled_only=enabled_only)
    
    # 处理响应，隐藏 API Key 并添加统计信息
    result = []
    for provider in providers:
        provider_dict = ProviderConfigResponse.model_validate(provider).model_dump()
        provider_dict["api_key"] = mask_api_key(provider.api_key)
        
        # 添加统计信息
        if include_stats:
            stats = await get_provider_statistics(db, provider.name)
            provider_dict["statistics"] = stats
        
        result.append(ProviderConfigResponse(**provider_dict))
    
    return result


@router.get("/providers/{provider_id}", response_model=ProviderConfigResponse)
async def get_provider(
    provider_id: UUID,
    include_stats: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """获取单个供应商配置"""
    provider = await get_provider_config(db, provider_id)
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    provider_dict = ProviderConfigResponse.model_validate(provider).model_dump()
    provider_dict["api_key"] = mask_api_key(provider.api_key)
    
    # 添加统计信息
    if include_stats:
        stats = await get_provider_statistics(db, provider.name)
        provider_dict["statistics"] = stats
    
    return ProviderConfigResponse(**provider_dict)


@router.post("/providers", response_model=ProviderConfigResponse, status_code=201)
async def create_provider(
    config: ProviderConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建供应商配置"""
    # 检查名称是否已存在
    from app.services.provider_service import get_provider_by_name
    existing = await get_provider_by_name(db, config.name)
    if existing:
        raise HTTPException(status_code=400, detail="Provider name already exists")
    
    provider = await create_provider_config(db, config)
    
    provider_dict = ProviderConfigResponse.model_validate(provider).model_dump()
    provider_dict["api_key"] = mask_api_key(provider.api_key)
    
    return ProviderConfigResponse(**provider_dict)


@router.put("/providers/{provider_id}", response_model=ProviderConfigResponse)
async def update_provider(
    provider_id: UUID,
    config: ProviderConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新供应商配置"""
    provider = await update_provider_config(db, provider_id, config)
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    provider_dict = ProviderConfigResponse.model_validate(provider).model_dump()
    provider_dict["api_key"] = mask_api_key(provider.api_key)
    
    return ProviderConfigResponse(**provider_dict)


@router.delete("/providers/{provider_id}")
async def delete_provider(
    provider_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """删除供应商配置"""
    success = await delete_provider_config(db, provider_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    return {"message": "Provider deleted successfully"}


@router.put("/providers/{provider_id}/toggle", response_model=ProviderConfigResponse)
async def toggle_provider(
    provider_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """切换供应商启用状态"""
    provider = await toggle_provider_config(db, provider_id)
    
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    
    provider_dict = ProviderConfigResponse.model_validate(provider).model_dump()
    provider_dict["api_key"] = mask_api_key(provider.api_key)
    
    return ProviderConfigResponse(**provider_dict)


class ModelsRequest(BaseModel):
    api_base_url: str
    api_key: str


@router.post("/models")
async def fetch_models(request: ModelsRequest):
    """获取 OpenAI 兼容 API 的模型列表"""
    try:
        # 构建请求 URL
        base_url = request.api_base_url.rstrip("/")
        if base_url.endswith("/v1"):
            endpoint = f"{base_url}/models"
        else:
            endpoint = f"{base_url}/v1/models"
        
        # 准备请求头
        headers = {
            "Authorization": f"Bearer {request.api_key}"
        }
        
        # 发送请求（无超时限制）
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.get(endpoint, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # OpenAI 格式: {"data": [{"id": "model-name", "object": "model", ...}, ...]}
                models = data.get("data", [])
                return {"data": models}
            else:
                error_msg = f"获取模型列表失败: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"].get("message", error_msg)
                except:
                    error_msg = f"{error_msg} - {response.text[:200]}"
                
                raise HTTPException(status_code=response.status_code, detail=error_msg)
    
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="请求超时，请检查 API Base URL")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"请求错误: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")


@router.get("/prompts/decision-test")
async def get_decision_test_prompts():
    """获取决策测试的提示文件内容"""
    try:
        # 获取 backend 目录的路径
        backend_dir = Path(__file__).parent.parent.parent
        system_prompt_path = backend_dir / "system-prompt-cycle-53.txt"
        user_prompt_path = backend_dir / "user-prompt-cycle-53.txt"
        
        system_content = ""
        user_content = ""
        
        # 读取 system prompt
        if system_prompt_path.exists():
            with open(system_prompt_path, 'r', encoding='utf-8') as f:
                system_content = f.read()
        else:
            raise HTTPException(status_code=404, detail=f"System prompt file not found: {system_prompt_path}")
        
        # 读取 user prompt
        if user_prompt_path.exists():
            with open(user_prompt_path, 'r', encoding='utf-8') as f:
                user_content = f.read()
        else:
            raise HTTPException(status_code=404, detail=f"User prompt file not found: {user_prompt_path}")
        
        return {
            "system_prompt": system_content,
            "user_prompt": user_content
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取提示文件失败: {str(e)}")

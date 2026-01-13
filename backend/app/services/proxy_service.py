import httpx
from typing import Dict, Any, Optional
from app.services.provider_service import get_active_provider, get_provider_by_name, get_decrypted_api_key
from app.services.logger_service import extract_tokens_from_response, generate_request_id
from sqlalchemy.ext.asyncio import AsyncSession
import time
import json
import traceback
import logging

logger = logging.getLogger(__name__)


async def proxy_request(
    db: AsyncSession,
    request_data: Dict[str, Any],
    user_id: Optional[str] = None,
    provider_name: Optional[str] = None,
    client_ip: Optional[str] = None
) -> tuple[Dict[str, Any], int, Optional[str], Dict[str, Any]]:
    """
    代理请求到配置的模型供应商
    
    返回: (响应数据, 状态码, 错误信息)
    """
    start_time = time.time()
    request_id = generate_request_id()
    
    # 获取供应商配置
    # 如果指定了供应商名称，使用指定的供应商；否则使用默认的活跃供应商
    provider = None
    if provider_name:
        provider = await get_provider_by_name(db, provider_name)
        if not provider:
            error_msg = f"Provider '{provider_name}' not found"
            return {"error": {"message": error_msg, "type": "invalid_request_error"}}, 404, error_msg, {}
        if not provider.is_enabled:
            error_msg = f"Provider '{provider_name}' is disabled"
            return {"error": {"message": error_msg, "type": "invalid_request_error"}}, 403, error_msg, {}
    else:
        provider = await get_active_provider(db)
        if not provider:
            error_msg = "No active provider configured"
            return {"error": {"message": error_msg, "type": "invalid_request_error"}}, 500, error_msg, {}
    
    # 检查IP白名单
    from app.services.whitelist_service import check_ip_whitelist
    from app.schemas.request_log import RequestLogCreate
    is_allowed, whitelist_error = await check_ip_whitelist(db, client_ip, provider.id)
    if not is_allowed:
        error_msg = whitelist_error or "IP address not in whitelist"
        log_data = RequestLogCreate(
            request_id=request_id,
            provider=provider.name,
            model=request_data.get("model", provider.default_model),
            request_params=request_data,
            response_content={"error": {"message": error_msg, "type": "access_denied"}},
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            duration_ms=0,
            status_code=403,
            error_message=error_msg,
            user_id=user_id,
            client_ip=client_ip
        )
        return {"error": {"message": error_msg, "type": "access_denied"}}, 403, error_msg, log_data
    
    # 获取解密后的 API Key
    try:
        api_key = get_decrypted_api_key(provider)
        if not api_key:
            error_msg = "API Key is empty or decryption failed"
            logger.error(error_msg)
            print(f"\n{'='*60}")
            print("ERROR: API Key is empty or decryption failed")
            print('='*60 + "\n")
            from app.schemas.request_log import RequestLogCreate
            log_data = RequestLogCreate(
                request_id=request_id,
                provider=provider.name if provider else "unknown",
                model=request_data.get("model", "unknown"),
                request_params=request_data,
                response_content={"error": error_msg},
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                duration_ms=0,
                status_code=500,
                error_message=error_msg,
                user_id=user_id,
                client_ip=client_ip
            )
            return {"error": error_msg}, 500, error_msg, log_data
    except Exception as e:
        error_msg = f"Failed to decrypt API Key: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        print(f"\n{'='*60}")
        print("ERROR: Failed to decrypt API Key")
        print('='*60)
        traceback.print_exc()
        print('='*60 + "\n")
        return {"error": error_msg}, 500, error_msg
    
    # 构建请求 URL
    base_url = provider.api_base_url.rstrip("/")
    # 如果 base_url 已经包含 /v1，则不再添加
    if base_url.endswith("/v1"):
        endpoint = f"{base_url}/chat/completions"
    else:
        endpoint = f"{base_url}/v1/chat/completions"
    
    # 准备请求数据
    proxy_request_data = request_data.copy()
    # 如果请求中没有指定模型，使用供应商的默认模型
    if "model" not in proxy_request_data or not proxy_request_data["model"]:
        proxy_request_data["model"] = provider.default_model
    
    # 准备请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # 调试信息：打印请求详情（不打印完整的 API Key）
    api_key_preview = api_key[:10] + "..." if len(api_key) > 10 else api_key
    logger.info(f"Request to {endpoint}")
    logger.info(f"Provider: {provider.name}")
    logger.info(f"API Key preview: {api_key_preview}")
    logger.info(f"Request data: {json.dumps(proxy_request_data, ensure_ascii=False)[:500]}")
    print(f"\n{'='*60}")
    print("REQUEST DETAILS:")
    print('='*60)
    print(f"Endpoint: {endpoint}")
    print(f"Provider: {provider.name}")
    print(f"API Key length: {len(api_key)}")
    print(f"API Key preview: {api_key_preview}")
    print(f"Model: {proxy_request_data.get('model', 'N/A')}")
    print(f"Messages count: {len(proxy_request_data.get('messages', []))}")
    print('='*60 + "\n")
    
    response_data = None
    status_code = 500
    error_message = None
    provider_request_id = None  # 在函数开始处初始化，确保所有代码路径都能访问
    
    try:
        # 发送请求（timeout=None 表示无超时限制）
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.post(
                endpoint,
                json=proxy_request_data,
                headers=headers
            )
            status_code = response.status_code
            
            # 提取供应商返回的 request id（无论成功还是失败）
            import re
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    # 尝试从成功响应中提取 request_id
                    if isinstance(response_data, dict) and "request_id" in response_data:
                        provider_request_id = str(response_data["request_id"])
                except:
                    response_data = response.json() if hasattr(response, 'json') else {}
            else:
                error_message = f"Provider returned status {response.status_code}: {response.text}"
                try:
                    response_data = response.json()
                    # 尝试从错误响应中提取 request id
                    if isinstance(response_data, dict):
                        # 从 error.message 中提取 request id
                        if "error" in response_data and isinstance(response_data["error"], dict):
                            error_msg = response_data["error"].get("message", "")
                            # 匹配 "request id: xxxxx" 或 "request_id: xxxxx" 格式
                            match = re.search(r'request[_\s]id[:\s]+([a-zA-Z0-9\-_]+)', error_msg, re.IGNORECASE)
                            if match:
                                provider_request_id = match.group(1)
                        # 也尝试从顶层获取 request_id
                        if not provider_request_id and "request_id" in response_data:
                            provider_request_id = str(response_data["request_id"])
                except:
                    response_data = {"error": error_message}
                    # 尝试从原始文本中提取 request id
                    match = re.search(r'request[_\s]id[:\s]+([a-zA-Z0-9\-_]+)', response.text, re.IGNORECASE)
                    if match:
                        provider_request_id = match.group(1)
                
                # 如果是 401 错误，提供更详细的错误信息
                if response.status_code == 401:
                    # 解析错误响应
                    error_detail = "Unknown error"
                    try:
                        error_json = response.json()
                        if isinstance(error_json, dict) and "error" in error_json:
                            error_obj = error_json["error"]
                            if "message" in error_obj:
                                error_detail = error_obj["message"]
                    except:
                        error_detail = response.text[:200]
                    
                    error_message = f"Authentication failed: {error_detail}"
                    logger.error(f"401 Unauthorized: {error_message}")
                    logger.error(f"Endpoint: {endpoint}")
                    logger.error(f"Provider: {provider.name}")
                    logger.error(f"API Base URL: {provider.api_base_url}")
                    logger.error(f"API Key length: {len(api_key)}")
                    logger.error(f"Full response: {response.text}")
                    
                    print(f"\n{'='*60}")
                    print("ERROR: 401 Unauthorized")
                    print('='*60)
                    print(f"Endpoint: {endpoint}")
                    print(f"Provider: {provider.name}")
                    print(f"API Base URL: {provider.api_base_url}")
                    print(f"API Key length: {len(api_key)}")
                    print(f"API Key preview: {api_key_preview}")
                    print(f"Model: {proxy_request_data.get('model', 'N/A')}")
                    print(f"Full response: {response.text}")
                    print(f"Response headers: {dict(response.headers)}")
                    print('='*60 + "\n")
                    
                    # 返回更详细的错误信息
                    response_data = {
                        "error": {
                            "message": error_detail,
                            "type": "authentication_error",
                            "status_code": 401,
                            "provider": provider.name,
                            "endpoint": endpoint
                        }
                    }
    
    except httpx.TimeoutException:
        error_message = "Request timeout"
        response_data = {"error": error_message}
        status_code = 504
        logger.error(f"Request timeout: {endpoint}")
    
    except httpx.RequestError as e:
        error_message = f"Request error: {str(e)}"
        response_data = {"error": error_message}
        status_code = 502
        logger.error(f"Request error: {error_message}")
        logger.error(traceback.format_exc())
        print(f"\n{'='*60}")
        print("ERROR: Request error")
        print('='*60)
        traceback.print_exc()
        print('='*60 + "\n")
    
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        response_data = {"error": error_message}
        status_code = 500
        logger.error(f"Unexpected error: {error_message}")
        logger.error(traceback.format_exc())
        print(f"\n{'='*60}")
        print("ERROR: Unexpected error")
        print('='*60)
        traceback.print_exc()
        print('='*60 + "\n")
    
    # 计算耗时
    duration_ms = int((time.time() - start_time) * 1000)
    
    # 提取 token 信息
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    
    if response_data and status_code == 200:
        prompt_tokens, completion_tokens, total_tokens = extract_tokens_from_response(response_data)
    
    # 计算计费（仅在成功时计算）
    billing_info = None
    if status_code == 200 and prompt_tokens > 0:
        from app.services.billing_service import calculate_cost
        billing_info = calculate_cost(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            provider=provider,
            user_discount_rate=None  # 可以从用户配置中获取，暂时使用默认值1.0
        )
    
    # 准备日志数据（异步记录，不阻塞响应）
    from app.schemas.request_log import RequestLogCreate
    log_data = RequestLogCreate(
        request_id=request_id,
        provider=provider.name,
        model=proxy_request_data.get("model", provider.default_model),
        request_params=proxy_request_data,
        response_content=response_data,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        duration_ms=duration_ms,
        status_code=status_code,
        error_message=error_message,
        user_id=user_id,
        # 计费信息
        actual_cost=billing_info["actual_cost"] if billing_info else None,
        model_rate=billing_info["model_rate"] if billing_info else None,
        completion_rate=billing_info["completion_rate"] if billing_info else None,
        group_rate=billing_info["group_rate"] if billing_info else None,
        recharge_rate=billing_info["recharge_rate"] if billing_info else None,
        user_discount_rate=billing_info["user_discount_rate"] if billing_info else None,
        provider_request_id=provider_request_id,
        client_ip=client_ip
    )
    
    # 返回响应数据，日志将在路由中异步记录
    return response_data, status_code, error_message, log_data


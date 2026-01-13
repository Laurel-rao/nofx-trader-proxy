from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import proxy, logs, config, stats, whitelist
from app.middleware.timing import TimingMiddleware

app = FastAPI(
    title=settings.app_name,
    description="AI 模型中转站 - 代理 OpenAI 格式请求到配置的模型供应商",
    version="1.0.0"
)

# 添加计时中间件
app.add_middleware(TimingMiddleware)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(proxy.router, prefix="/v1", tags=["proxy"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(config.router, prefix="/api/config", tags=["config"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(whitelist.router, prefix="/api/whitelist", tags=["whitelist"])

# 调试：打印所有路由
if settings.debug:
    print("\n=== 注册的路由 ===")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"{list(route.methods)} {route.path}")
    print("==================\n")


@app.get("/")
async def root():
    return {
        "message": "AI Proxy Server",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# 调试路由（仅在开发模式下）
if settings.debug:
    @app.get("/debug/routes")
    async def debug_routes():
        """调试：查看所有注册的路由"""
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append({
                    "path": route.path,
                    "methods": list(route.methods),
                    "name": getattr(route, 'name', None)
                })
        return {"routes": routes}

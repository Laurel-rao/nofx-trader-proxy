from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # 数据库配置
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/proxy_openai"
    
    # 加密密钥（用于加密 API Key）
    encryption_key: str = "your-secret-key-change-in-production"
    
    # CORS 配置（环境变量中为逗号分隔的字符串）
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    
    # 应用配置
    app_name: str = "AI Proxy Server"
    debug: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """获取 CORS origins 列表（从逗号分隔的字符串转换为列表）"""
        if not self.cors_origins:
            return ["http://localhost:5173", "http://localhost:3000"]
        return [origin.strip() for origin in self.cors_origins.split(',') if origin.strip()]


settings = Settings()


#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库（如果不存在）
"""
import asyncio
import asyncpg
from urllib.parse import urlparse
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings


def parse_database_url(url: str) -> dict:
    """解析数据库 URL"""
    # 移除 postgresql+asyncpg:// 前缀
    if url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql+asyncpg://", "postgresql://")
    elif url.startswith("postgresql://"):
        pass
    else:
        raise ValueError(f"不支持的数据库 URL 格式: {url}")
    
    parsed = urlparse(url)
    return {
        "user": parsed.username or "postgres",
        "password": parsed.password or "",
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/") if parsed.path else "postgres"
    }


async def create_database():
    """创建数据库（如果不存在）"""
    # 解析数据库 URL
    db_config = parse_database_url(settings.database_url)
    target_db = db_config["database"]
    
    # 连接到默认的 postgres 数据库来创建新数据库
    admin_config = db_config.copy()
    admin_config["database"] = "postgres"
    
    print(f"正在连接到 PostgreSQL 服务器: {admin_config['host']}:{admin_config['port']}")
    print(f"目标数据库: {target_db}")
    
    try:
        # 连接到 postgres 数据库
        conn = await asyncpg.connect(
            host=admin_config["host"],
            port=admin_config["port"],
            user=admin_config["user"],
            password=admin_config["password"],
            database=admin_config["database"]
        )
        
        # 检查数据库是否存在
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            target_db
        )
        
        if exists:
            print(f"✓ 数据库 '{target_db}' 已存在")
            await conn.close()
            return True
        
        # 创建数据库
        print(f"正在创建数据库 '{target_db}'...")
        await conn.execute(f'CREATE DATABASE "{target_db}"')
        print(f"✓ 数据库 '{target_db}' 创建成功")
        
        await conn.close()
        return True
        
    except asyncpg.exceptions.InvalidPasswordError:
        print(f"❌ 错误: 数据库密码错误")
        print(f"请检查 .env 文件中的 DATABASE_URL 配置")
        return False
    except asyncpg.exceptions.ConnectionRefusedError:
        print(f"❌ 错误: 无法连接到 PostgreSQL 服务器")
        print(f"请确保 PostgreSQL 服务正在运行")
        return False
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


async def main():
    """主函数"""
    print("=" * 50)
    print("数据库初始化脚本")
    print("=" * 50)
    print()
    
    success = await create_database()
    
    if success:
        print()
        print("=" * 50)
        print("✓ 数据库初始化完成")
        print("=" * 50)
        print()
        print("下一步: 运行数据库迁移")
        print("  cd backend")
        print("  alembic upgrade head")
        sys.exit(0)
    else:
        print()
        print("=" * 50)
        print("❌ 数据库初始化失败")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())


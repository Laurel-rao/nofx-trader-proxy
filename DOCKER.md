# Docker 部署指南

## 快速开始

### 1. 准备环境变量

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置 `ENCRYPTION_KEY` 等配置。

### 2. 启动服务

```bash
docker-compose up -d
```

### 3. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f nginx
```

### 4. 停止服务

```bash
docker-compose down
```

### 5. 清理数据（包括数据库）

```bash
docker-compose down -v
```

## 服务说明

### PostgreSQL
- 端口: 5432
- 数据库: proxy_openai
- 用户: postgres
- 密码: postgres（生产环境请修改）

### Backend API
- 内部端口: 8000
- 健康检查: http://localhost:8000/health
- API 文档: http://localhost:8000/docs

### Frontend
- 构建后由 Nginx 提供静态文件服务

### Nginx
- HTTP 端口: 80
- 前端访问: http://localhost/
- API 代理: http://localhost/api/ 和 http://localhost/v1/

## 数据库迁移

数据库迁移会在后端服务启动时自动执行：

```bash
alembic upgrade head
```

如果需要手动执行迁移：

```bash
docker-compose exec backend alembic upgrade head
```

## 开发模式

如果需要挂载代码进行开发，docker-compose.yaml 中已经配置了 volumes。

修改代码后，后端服务会自动重载（如果使用 uvicorn 的 reload 模式）。

## 生产环境建议

1. **修改数据库密码**：在 docker-compose.yaml 中修改 `POSTGRES_PASSWORD`
2. **修改加密密钥**：在 `.env` 文件中设置强密码
3. **配置 HTTPS**：添加 SSL 证书配置到 Nginx
4. **限制资源**：在 docker-compose.yaml 中添加资源限制
5. **配置备份**：定期备份 PostgreSQL 数据卷

## 常用命令

```bash
# 重新构建镜像
docker-compose build

# 重新构建并启动
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 进入容器
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres -d proxy_openai

# 查看数据库
docker-compose exec postgres psql -U postgres -d proxy_openai -c "SELECT * FROM provider_configs;"
```


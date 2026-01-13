# AI 模型中转站

一个基于 FastAPI + Vue3 的 AI 模型中转站系统，负责接收 OpenAI 类型的参数，并转发至配置的 AI 模型供应商，中间记录每次参数和每次返回，并记录时长。

## 功能特性

- ✅ 代理 OpenAI 格式的请求到配置的模型供应商
- ✅ 完整记录每次请求的参数和响应
- ✅ 记录请求耗时和 Token 使用量
- ✅ 供应商配置管理（支持多个供应商，优先级配置）
- ✅ 请求日志查看、筛选、搜索
- ✅ 统计监控（请求量、Token 使用、模型使用情况等）
- ✅ 数据导出（CSV/JSON 格式）
- ✅ API Key 加密存储

## 技术栈

### 后端
- FastAPI - Web 框架
- SQLAlchemy - ORM
- Alembic - 数据库迁移
- PostgreSQL - 数据库
- httpx - HTTP 客户端
- cryptography - 加密库

### 前端
- Vue 3 - 前端框架
- Vue Router - 路由管理
- Pinia - 状态管理
- Element Plus - UI 组件库
- ECharts - 图表库
- Axios - HTTP 客户端

## 项目结构

```
proxy_openai/
├── backend/                 # 后端项目
│   ├── app/
│   │   ├── models/         # 数据库模型
│   │   ├── schemas/        # Pydantic 模型
│   │   ├── services/       # 业务逻辑服务
│   │   ├── routers/        # API 路由
│   │   ├── middleware/     # 中间件
│   │   ├── config.py       # 配置管理
│   │   ├── database.py     # 数据库连接
│   │   └── main.py         # 应用入口
│   ├── alembic/            # 数据库迁移
│   └── requirements.txt    # Python 依赖
└── frontend/               # 前端项目
    ├── src/
    │   ├── views/          # 页面组件
    │   ├── components/     # 通用组件
    │   ├── api/            # API 接口
    │   ├── router/         # 路由配置
    │   └── utils/          # 工具函数
    └── package.json        # Node 依赖
```

## 快速开始

### 1. 环境要求

- Python 3.9+
- Node.js 16+
- PostgreSQL 12+

### 2. 后端设置

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
# 注意: 将 POSTGRESQL_PASSWORD 替换为实际的数据库密码

# 创建数据库（如果不存在）
python init_db.py

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- 前端界面: http://localhost:5173
- API 文档: http://localhost:8000/docs
- 代理端点: http://localhost:8000/v1/chat/completions

## 使用说明

### 配置供应商

1. 访问前端界面，进入"配置管理"
2. 点击"添加供应商"
3. 填写供应商信息：
   - 供应商名称（如：OpenAI）
   - API Base URL（如：https://api.openai.com）
   - API Key
   - 默认模型（如：gpt-3.5-turbo）
   - 优先级（数字越小优先级越高）

### 使用代理 API

代理 API 完全兼容 OpenAI 的 Chat Completions API：

```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### 查看日志和统计

- **请求日志**: 查看所有请求记录，支持筛选、搜索
- **统计监控**: 查看请求量、Token 使用、模型使用情况等统计信息
- **数据导出**: 支持导出为 CSV 或 JSON 格式

## API 接口

### 代理接口
- `POST /v1/chat/completions` - 代理 OpenAI Chat Completions API

### 日志接口
- `GET /api/logs` - 获取日志列表
- `GET /api/logs/{log_id}` - 获取日志详情
- `DELETE /api/logs/{log_id}` - 删除日志

### 配置接口
- `GET /api/config/providers` - 获取供应商列表
- `POST /api/config/providers` - 创建供应商
- `PUT /api/config/providers/{provider_id}` - 更新供应商
- `DELETE /api/config/providers/{provider_id}` - 删除供应商
- `PUT /api/config/providers/{provider_id}/toggle` - 切换启用状态

### 统计接口
- `GET /api/stats/summary` - 获取统计摘要
- `GET /api/stats/timeline` - 获取时间线统计
- `GET /api/stats/tokens` - Token 使用统计
- `GET /api/stats/models` - 模型使用统计

## 数据库设计

### request_logs 表
- id (UUID)
- created_at (Timestamp)
- request_id (String, 唯一)
- provider (String)
- model (String)
- request_params (JSONB)
- response_content (JSONB)
- prompt_tokens (Integer)
- completion_tokens (Integer)
- total_tokens (Integer)
- duration_ms (Integer)
- status_code (Integer)
- error_message (Text)
- user_id (String)

### provider_configs 表
- id (UUID)
- name (String, 唯一)
- api_base_url (String)
- api_key (String, 加密存储)
- default_model (String)
- is_enabled (Boolean)
- priority (Integer)
- created_at (Timestamp)
- updated_at (Timestamp)

## 注意事项

1. **API Key 加密**: 所有 API Key 都使用 Fernet 对称加密存储
2. **异步日志**: 日志记录使用后台任务，不阻塞请求响应
3. **CORS 配置**: 默认允许 localhost:5173 和 localhost:3000，生产环境需要修改
4. **数据库迁移**: 使用 Alembic 管理数据库迁移，修改模型后需要生成新的迁移文件

## 开发

### 生成数据库迁移

```bash
cd backend
alembic revision --autogenerate -m "描述信息"
alembic upgrade head
```

### 构建前端

```bash
cd frontend
npm run build
```

## 许可证

MIT


# 修复 API 连接问题

## 问题描述
前端在 Docker 部署后，仍然尝试访问 `http://localhost:8000/api/logs`，导致 `ERR_CONNECTION_REFUSED` 错误。

## 原因
前端代码在构建时没有正确识别生产环境，导致使用了开发环境的 API 地址。

## 解决方案

### 方法 1: 使用更新脚本（推荐）
```bash
./update.sh --rebuild
```

### 方法 2: 手动重新构建前端
```bash
# 停止服务
docker-compose down

# 重新构建前端镜像
docker-compose build --no-cache frontend

# 启动服务
docker-compose up -d
```

### 方法 3: 仅重建前端容器
```bash
# 删除前端容器和镜像
docker-compose rm -f frontend
docker rmi proxy_openai-frontend 2>/dev/null || true

# 重新构建并启动
docker-compose up -d --build frontend
```

## 验证修复

1. 重新构建后，检查前端构建产物：
```bash
docker-compose exec frontend ls -la /usr/share/nginx/html
```

2. 检查浏览器控制台，应该看到：
   - ✅ `GET /api/logs?page=1&page_size=10` (相对路径)
   - ❌ 不再有 `GET http://localhost:8000/api/logs` 错误

3. 检查网络请求：
   - 打开浏览器开发者工具
   - 查看 Network 标签
   - API 请求应该使用相对路径 `/api/...`

## 已修复的配置

1. **frontend/src/api/request.js**
   - 生产环境自动使用相对路径
   - 开发环境使用 `http://localhost:8000`

2. **frontend/Dockerfile**
   - 设置 `NODE_ENV=production`
   - 使用 `--mode production` 构建

3. **frontend/vite.config.js**
   - 添加构建配置确保生产模式

4. **docker-compose.yaml**
   - 传递 `VITE_API_BASE_URL=""` 构建参数

## 注意事项

- 重新构建后，前端会通过 nginx 代理访问 API
- API 请求路径：`/api/...` → nginx → `http://backend:8000/api/...`
- 确保 nginx 容器正常运行


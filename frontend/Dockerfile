FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制 package 文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 设置构建时环境变量（使用相对路径，因为通过 nginx 代理）
# Vite 需要在构建时设置环境变量
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
# 确保使用生产模式构建
ENV NODE_ENV=production

# 清理旧的构建产物和缓存
RUN rm -rf dist .vite node_modules/.vite

# 添加构建时间戳，确保每次构建都不同
RUN echo "Build time: $(date -u +%Y-%m-%dT%H:%M:%SZ)" > /app/build-info.txt

# 构建生产版本（明确指定模式，强制重新构建）
RUN npm run build -- --mode production --force

# 验证构建产物
RUN ls -lah dist/ && echo "构建完成，文件列表：" && find dist -type f -name "*.js" | head -5

# 输出阶段 - 将构建产物复制到指定目录
FROM alpine:latest

# 安装必要的工具
RUN apk add --no-cache bash rsync

# 创建输出目录
RUN mkdir -p /usr/share/nginx/html /app/dist

# 从构建阶段复制构建产物到临时目录
COPY --from=builder /app/dist /app/dist

# 启动脚本：将构建产物同步到 volume 挂载点
CMD ["sh", "-c", "
  echo '同步构建产物到 volume...' && \
  rsync -av --delete /app/dist/ /usr/share/nginx/html/ && \
  echo '构建产物同步完成' && \
  ls -la /usr/share/nginx/html && \
  while true; do sleep 3600; done
"]


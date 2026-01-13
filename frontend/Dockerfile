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

# 构建生产版本（明确指定模式）
RUN npm run build -- --mode production

# 输出阶段 - 将构建产物复制到指定目录
FROM alpine:latest

# 安装必要的工具
RUN apk add --no-cache bash

# 创建输出目录
RUN mkdir -p /usr/share/nginx/html

# 从构建阶段复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 保持容器运行（用于复制文件到 volume）
CMD ["sh", "-c", "while true; do sleep 3600; done"]


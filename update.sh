#!/bin/bash

# 更新脚本 - Git Pull 并更新 Docker 容器
# 使用方法: 
#   ./update.sh          # 默认更新（拉取代码并重建容器）
#   ./update.sh --pull-only   # 仅拉取代码，不更新 Docker
#   ./update.sh --no-pull     # 不拉取代码，仅更新 Docker
#   ./update.sh --rebuild     # 强制重新构建（不使用缓存）

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否在 Git 仓库中
if [ ! -d ".git" ]; then
    log_error "当前目录不是 Git 仓库！"
    exit 1
fi

# 检查 Docker 和 Docker Compose 是否安装
if ! command -v docker &> /dev/null; then
    log_error "Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    log_error "Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检测 docker-compose 命令
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# 解析命令行参数
PULL_CODE=true
UPDATE_DOCKER=true
REBUILD_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --pull-only)
            PULL_CODE=true
            UPDATE_DOCKER=false
            shift
            ;;
        --no-pull)
            PULL_CODE=false
            UPDATE_DOCKER=true
            shift
            ;;
        --rebuild)
            REBUILD_FLAG="--no-cache"
            shift
            ;;
        -h|--help)
            echo "使用方法: ./update.sh [选项]"
            echo ""
            echo "选项:"
            echo "  --pull-only    仅拉取代码，不更新 Docker"
            echo "  --no-pull      不拉取代码，仅更新 Docker"
            echo "  --rebuild      强制重新构建（不使用缓存）"
            echo "  -h, --help     显示帮助信息"
            exit 0
            ;;
        *)
            log_error "未知参数: $1"
            echo "使用 --help 查看帮助信息"
            exit 1
            ;;
    esac
done

log_info "开始更新流程..."

# 1. 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    log_warning "检测到未提交的更改："
    git status --short
    read -p "是否继续更新？未提交的更改可能会被覆盖 (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "更新已取消"
        exit 0
    fi
fi

# 2. 获取当前分支
CURRENT_BRANCH=$(git branch --show-current)
log_info "当前分支: $CURRENT_BRANCH"

# 3. Git Pull
if [ "$PULL_CODE" = true ]; then
    log_info "正在拉取最新代码..."
    OLD_COMMIT=$(git rev-parse HEAD)
    if git pull origin "$CURRENT_BRANCH"; then
        NEW_COMMIT=$(git rev-parse HEAD)
        if [ "$OLD_COMMIT" != "$NEW_COMMIT" ]; then
            log_success "代码拉取成功 (更新了提交)"
        else
            log_info "代码已是最新版本"
        fi
    else
        log_error "代码拉取失败"
        exit 1
    fi
else
    log_info "跳过代码拉取（使用 --no-pull 选项）"
fi

# 4. 更新 Docker 容器
if [ "$UPDATE_DOCKER" = true ]; then
    log_info "开始更新 Docker 容器..."
    
    # 5. 停止现有容器（可选，保留数据）
    log_info "停止现有容器..."
    $DOCKER_COMPOSE down || true
    
    # 6. 重新构建镜像
    log_info "重新构建 Docker 镜像..."
    BUILD_CMD="$DOCKER_COMPOSE build"
    if [ -n "$REBUILD_FLAG" ]; then
        BUILD_CMD="$BUILD_CMD $REBUILD_FLAG"
        log_info "使用 --no-cache 强制重新构建"
    fi
    
    if eval $BUILD_CMD; then
        log_success "镜像构建成功"
    else
        log_error "镜像构建失败"
        exit 1
    fi
    
    # 7. 启动容器
    log_info "启动 Docker 容器..."
    if $DOCKER_COMPOSE up -d; then
        log_success "容器启动成功"
    else
        log_error "容器启动失败"
        exit 1
    fi
    
    # 8. 等待服务就绪
    log_info "等待服务就绪..."
    sleep 5
    
    # 9. 检查服务状态
    log_info "检查服务状态..."
    $DOCKER_COMPOSE ps
    
    # 10. 显示日志（可选）
    log_info "显示最近的服务日志..."
    $DOCKER_COMPOSE logs --tail=50
    
    log_success "更新完成！"
    log_info "访问地址:"
    log_info "  前端: http://localhost/"
    log_info "  API: http://localhost/api/"
    log_info "  API 文档: http://localhost/docs"
else
    log_info "跳过 Docker 更新（使用 --pull-only 选项）"
fi


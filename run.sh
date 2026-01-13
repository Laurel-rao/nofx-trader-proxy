#!/bin/bash

# AI 模型中转站启动脚本

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  AI 模型中转站启动脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}错误: 未找到 python3，请先安装 Python 3.9+${NC}"
    exit 1
fi

# 检查 Node.js 环境
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}错误: 未找到 node，请先安装 Node.js 16+${NC}"
    exit 1
fi

# 函数：启动后端
start_backend() {
    echo -e "${GREEN}启动后端服务...${NC}"
    
    # 检查并激活虚拟环境（优先使用根目录的 .venv）
    if [ -d ".venv" ]; then
        echo -e "${GREEN}使用根目录虚拟环境 .venv${NC}"
        source .venv/bin/activate
    elif [ -d "backend/venv" ]; then
        echo -e "${GREEN}使用 backend/venv 虚拟环境${NC}"
        source backend/venv/bin/activate
    elif [ -d "backend/.venv" ]; then
        echo -e "${GREEN}使用 backend/.venv 虚拟环境${NC}"
        source backend/.venv/bin/activate
    else
        echo -e "${YELLOW}未找到虚拟环境，请先创建虚拟环境${NC}"
        echo -e "${YELLOW}建议在项目根目录运行: python3 -m venv .venv${NC}"
        exit 1
    fi
    
    cd backend
    
    # 安装依赖
    if [ ! -f ".deps_installed" ]; then
        echo -e "${YELLOW}安装后端依赖...${NC}"
        pip install -r requirements.txt
        touch .deps_installed
    fi
    
    # 检查环境变量文件
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}警告: 未找到 .env 文件，使用默认配置${NC}"
        if [ -f ".env.example" ]; then
            cp .env.example .env
            echo -e "${YELLOW}已从 .env.example 创建 .env 文件，请编辑配置${NC}"
            echo -e "${YELLOW}请编辑 .env 文件，将 POSTGRESQL_PASSWORD 替换为实际密码${NC}"
        fi
    fi
    
    # 检查数据库是否存在，如果不存在则创建
    echo -e "${YELLOW}检查数据库...${NC}"
    python init_db.py 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}数据库检查失败，请手动运行: python init_db.py${NC}"
        echo -e "${YELLOW}或确保数据库已存在并配置正确${NC}"
    fi
    
    # 启动服务
    echo -e "${GREEN}后端服务启动在 http://localhost:8000${NC}"
    echo -e "${GREEN}API 文档: http://localhost:8000/docs${NC}"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../.backend_pid
    cd ..
}

# 函数：启动前端
start_frontend() {
    echo -e "${GREEN}启动前端服务...${NC}"
    cd frontend
    
    # 检查 node_modules
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}安装前端依赖...${NC}"
        npm install
    fi
    
    # 启动服务
    echo -e "${GREEN}前端服务启动在 http://localhost:5173${NC}"
    npm run dev &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../.frontend_pid
    cd ..
}

# 函数：停止服务
stop_services() {
    echo -e "${YELLOW}停止服务...${NC}"
    
    if [ -f ".backend_pid" ]; then
        BACKEND_PID=$(cat .backend_pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill $BACKEND_PID
            echo -e "${GREEN}后端服务已停止${NC}"
        fi
        rm -f .backend_pid
    fi
    
    if [ -f ".frontend_pid" ]; then
        FRONTEND_PID=$(cat .frontend_pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill $FRONTEND_PID
            echo -e "${GREEN}前端服务已停止${NC}"
        fi
        rm -f .frontend_pid
    fi
    
    # 清理可能残留的进程
    pkill -f "uvicorn app.main:app" 2>/dev/null
    pkill -f "vite" 2>/dev/null
}

# 函数：检查服务状态
check_status() {
    echo -e "${BLUE}服务状态:${NC}"
    
    if [ -f ".backend_pid" ]; then
        BACKEND_PID=$(cat .backend_pid)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 后端服务运行中 (PID: $BACKEND_PID)${NC}"
        else
            echo -e "${YELLOW}✗ 后端服务未运行${NC}"
        fi
    else
        echo -e "${YELLOW}✗ 后端服务未运行${NC}"
    fi
    
    if [ -f ".frontend_pid" ]; then
        FRONTEND_PID=$(cat .frontend_pid)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 前端服务运行中 (PID: $FRONTEND_PID)${NC}"
        else
            echo -e "${YELLOW}✗ 前端服务未运行${NC}"
        fi
    else
        echo -e "${YELLOW}✗ 前端服务未运行${NC}"
    fi
}

# 主逻辑
case "$1" in
    start)
        start_backend
        sleep 2
        start_frontend
        echo ""
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  服务启动完成！${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo -e "${BLUE}后端: http://localhost:8000${NC}"
        echo -e "${BLUE}前端: http://localhost:5173${NC}"
        echo -e "${BLUE}API 文档: http://localhost:8000/docs${NC}"
        echo ""
        echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
        wait
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_backend
        sleep 2
        start_frontend
        ;;
    status)
        check_status
        ;;
    backend)
        start_backend
        echo ""
        echo -e "${GREEN}后端服务运行中，按 Ctrl+C 停止${NC}"
        wait
        ;;
    frontend)
        start_frontend
        wait
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status|backend|frontend}"
        echo ""
        echo "命令说明:"
        echo "  start     - 启动后端和前端服务"
        echo "  stop      - 停止所有服务"
        echo "  restart   - 重启所有服务"
        echo "  status    - 查看服务状态"
        echo "  backend   - 仅启动后端服务"
        echo "  frontend  - 仅启动前端服务"
        exit 1
        ;;
esac


#!/bin/bash

# 代理商销售系统 - WSL 一键部署脚本
# 在WSL中运行此脚本

set -e

echo "=========================================="
echo "   代理商销售系统 - WSL部署"
echo "=========================================="
echo ""

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查是否在WSL中
if ! grep -qi "microsoft\|wsl" /proc/version 2>/dev/null; then
    echo -e "${YELLOW}⚠️  检测到可能不在WSL环境中${NC}"
    read -p "是否继续? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}❌ Python3 未安装${NC}"
    echo "请安装: sudo apt install python3 python3-venv"
    exit 1
fi

echo -e "${GREEN}✅ Python3 已安装${NC}"

# 检查文件
if [ ! -f "backend/main.py" ]; then
    echo -e "${YELLOW}❌ 后端文件不存在${NC}"
    echo "请确保以下文件在当前目录:"
    echo "  - backend/main.py"
    echo "  - backend/requirements.txt"
    echo "  - backend/data.db"
    echo "  - frontend/dist/"
    exit 1
fi

echo -e "${GREEN}✅ 文件检查通过${NC}"

# 创建虚拟环境
echo ""
echo "【1】创建虚拟环境..."
if [ ! -d "backend/venv" ]; then
    cd backend
    python3 -m venv venv
    cd ..
    echo "   虚拟环境创建完成"
else
    echo "   虚拟环境已存在"
fi

# 安装依赖
echo ""
echo "【2】安装依赖..."
cd backend
source venv/bin/activate
pip install -r requirements.txt -q
cd ..
echo -e "${GREEN}✅ 依赖安装完成${NC}"

# 启动后端
echo ""
echo "【3】启动后端服务 (端口 8000)..."
cd backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

sleep 2

# 检查后端
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端启动成功${NC}"
else
    echo -e "${YELLOW}⚠️ 后端启动中...${NC}"
fi

# 启动前端
echo ""
echo "【4】启动前端服务 (端口 5174)..."
if [ -d "frontend/dist" ]; then
    cd frontend/dist
    nohup python3 -m http.server 5174 --bind 0.0.0.0 > /tmp/frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ../..

    sleep 1

    if curl -s http://localhost:5174 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端启动成功${NC}"
    else
        echo -e "${YELLOW}⚠️ 前端启动中...${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ 前端目录不存在，跳过前端启动${NC}"
fi

echo ""
echo "=========================================="
echo "   ✅ 部署完成！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  - 前端页面: http://localhost:5174"
echo "  - API文档: http://localhost:8000/docs"
echo ""
echo "测试账号:"
echo "  - 管理员: admin / admin123"
echo "  - 销售: sales1 / sales123"
echo "  - 代理商: agent1 / agent123"
echo "  - 客户: customer1 / cust123"
echo ""
echo "服务进程:"
echo "  - 后端 PID: $BACKEND_PID"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "  - 前端 PID: $FRONTEND_PID"
fi
echo ""
echo "停止服务:"
echo "  - kill $BACKEND_PID"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "  - kill $FRONTEND_PID"
fi
echo ""

# 保存PID到文件
echo "$BACKEND_PID $FRONTEND_PID" > /tmp/agent-system.pids

exit 0
#!/bin/bash

# 代理商销售系统 - WSL一键安装脚本
# 用法: ./install_for_wsl.sh

set -e

echo "=========================================="
echo "   代理商销售系统 - WSL安装脚本"
echo "=========================================="
echo ""

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 项目目录
PROJECT_DIR=~/agent-system

# 1. 创建目录
echo "【1】创建目录..."
mkdir -p $PROJECT_DIR/backend
mkdir -p $PROJECT_DIR/frontend/dist
echo "   ✅ 目录创建完成"

# 2. 复制文件（如果当前目录有项目）
if [ -f "backend/main.py" ]; then
    echo ""
    echo "【2】复制项目文件..."
    cp -r backend/* $PROJECT_DIR/backend/
    cp -r frontend/dist/* $PROJECT_DIR/frontend/dist/
    echo "   ✅ 文件复制完成"
elif [ -f "main.py" ]; then
    echo ""
    echo "【2】复制项目文件..."
    cp -r backend/* $PROJECT_DIR/backend/ 2>/dev/null || true
    cp -r frontend/dist/* $PROJECT_DIR/frontend/dist/ 2>/dev/null || true
    cp -r app/* $PROJECT_DIR/backend/app/ 2>/dev/null || true
    echo "   ✅ 文件复制完成"
else
    echo ""
    echo "【2】请确保当前目录包含项目文件"
    echo "   需要的文件: backend/main.py, frontend/dist/"
    echo ""
    echo "   如果是从GitHub clone的，请先运行:"
    echo "   git clone https://github.com/kaungyang11/agent-system.git"
    echo "   cd agent-system"
    echo "   ./install_for_wsl.sh"
    exit 1
fi

# 3. 安装Python依赖
echo ""
echo "【3】安装Python依赖..."
cd $PROJECT_DIR/backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt
echo "   ✅ 依赖安装完成"

# 4. 启动后端
echo ""
echo "【4】启动后端服务 (端口 8000)..."
cd $PROJECT_DIR/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/agent-backend.log 2>&1 &
BACKEND_PID=$!
echo "   ✅ 后端已启动 (PID: $BACKEND_PID)"

sleep 2

# 检查后端是否启动成功
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "   ✅ 后端API正常"
else
    echo "   ⚠️ 后端启动中..."
fi

# 5. 启动前端
echo ""
echo "【5】启动前端服务 (端口 5174)..."
cd $PROJECT_DIR/frontend/dist
nohup python3 -m http.server 5174 --bind 0.0.0.0 > /tmp/agent-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   ✅ 前端已启动 (PID: $FRONTEND_PID)"

sleep 1

if curl -s http://localhost:5174 > /dev/null 2>&1; then
    echo "   ✅ 前端页面正常"
else
    echo "   ⚠️ 前端启动中..."
fi

# 完成
echo ""
echo "=========================================="
echo "   ✅ 安装完成！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "   - 前端页面: http://localhost:5174"
echo "   - API文档: http://localhost:8000/docs"
echo ""
echo "测试账号:"
echo "   - 管理员: admin / admin123"
echo "   - 销售: sales1 / sales123"
echo "   - 代理商: agent1 / agent123"
echo "   - 客户: customer1 / cust123"
echo ""
echo "停止服务:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""

exit 0
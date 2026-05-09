#!/bin/bash

# 代理商销售管理系统 - 一键启动脚本

echo "🚀 代理商销售管理系统启动中..."
echo "================================"

# 检查是否在backend目录
if [ ! -f "main.py" ]; then
    echo "❌ 请在 agent-system/backend 目录下运行此脚本"
    exit 1
fi

# 检查并创建虚拟环境
if [ ! -d "../venv" ]; then
    echo "📦 正在创建虚拟环境..."
    cd ..
    python3 -m venv venv
    cd backend
fi

# 激活虚拟环境并安装依赖
echo "📦 安装后端依赖..."
source ../venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null

# 启动后端
echo "🚀 启动后端服务..."
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ 后端已启动 (PID: $BACKEND_PID, http://localhost:8000)"

# 等待后端启动
sleep 3

# 切换到前端目录
echo "🎨 启动前端服务..."
cd ../frontend

# 检查是否安装了依赖
if [ ! -d "node_modules" ]; then
    echo "📦 正在安装前端依赖..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "✅ 前端已启动 (PID: $FRONTEND_PID, http://localhost:5173)"

echo ""
echo "================================"
echo "🎉 启动完成！"
echo ""
echo "📝 后端: http://localhost:8000"
echo "📝 前端: http://localhost:5173"
echo ""
echo "🛑 停止服务: 按 Ctrl+C"
echo "================================"

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
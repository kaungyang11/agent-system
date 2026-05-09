#!/bin/bash

# 代理商销售管理系统 - 一键启动脚本

echo "🚀 代理商销售管理系统启动中..."
echo "================================"

# 确定项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 检查是否在backend目录，如果在根目录则切换
if [ -f "backend/main.py" ]; then
    # 在根目录
    BACKEND_DIR="$SCRIPT_DIR/backend"
    FRONTEND_DIR="$SCRIPT_DIR/frontend"
elif [ -f "main.py" ]; then
    # 已在backend目录
    BACKEND_DIR="$SCRIPT_DIR"
    FRONTEND_DIR="$SCRIPT_DIR/../frontend"
else
    echo "❌ 请在 agent-system 目录下运行此脚本"
    exit 1
fi

# 检查并重新创建虚拟环境（修复依赖问题）
echo "🔧 检查虚拟环境..."
if [ ! -d "$SCRIPT_DIR/venv" ] || ! "$SCRIPT_DIR/venv/bin/python" -c "import passlib" 2>/dev/null; then
    echo "📦 正在创建/修复虚拟环境..."
    rm -rf "$SCRIPT_DIR/venv"
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# 安装后端依赖
echo "📦 安装后端依赖..."
source "$SCRIPT_DIR/venv/bin/activate"
pip install -q -r "$BACKEND_DIR/requirements.txt"

# 启动后端
echo "🚀 启动后端服务..."
cd "$BACKEND_DIR"
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ 后端已启动 (PID: $BACKEND_PID, http://localhost:8000)"

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动前端服务..."
cd "$FRONTEND_DIR"

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
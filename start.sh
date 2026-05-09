#!/bin/bash

# 代理商销售管理系统 - 启动脚本
# 用于 SophCLAW 终端环境

echo "🚀 启动代理商销售管理系统..."
echo "================================"

# 检查端口是否被占用
check_port() {
    if lsof -i:$1 > /dev/null 2>&1; then
        echo "⚠️ 端口 $1 已被占用"
        return 1
    fi
    return 0
}

# 启动后端服务
start_backend() {
    echo ""
    echo "📦 启动后端服务 (端口 8000)..."
    cd backend
    
    # 检查依赖
    if [ ! -d "venv" ]; then
        echo "   创建虚拟环境..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt -q
    fi
    
    # 启动 uvicorn
    source venv/bin/activate
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    
    sleep 2
    
    if curl -s http://localhost:8000/api/health > /dev/null; then
        echo "   ✅ 后端启动成功!"
        echo "   📖 API文档: http://localhost:8000/docs"
    else
        echo "   ❌ 后端启动失败，查看日志: backend.log"
    fi
}

# 启动前端服务
start_frontend() {
    echo ""
    echo "🎨 启动前端服务 (端口 5174)..."
    cd frontend/dist
    
    nohup python3 -m http.server 5174 --bind 0.0.0.0 > ../frontend.log 2>&1 &
    
    sleep 2
    
    if curl -s http://localhost:5174 > /dev/null; then
        echo "   ✅ 前端启动成功!"
        echo "   🌐 访问地址: http://localhost:5174"
    else
        echo "   ❌ 前端启动失败，查看日志: frontend.log"
    fi
}

# 主程序
case "$1" in
    backend)
        start_backend
        ;;
    frontend)
        start_frontend
        ;;
    all|"")
        start_backend
        start_frontend
        ;;
    status)
        echo ""
        echo "📊 服务状态:"
        echo "================================"
        if curl -s http://localhost:8000/api/health > /dev/null; then
            echo "  ✅ 后端: 运行中 (http://localhost:8000)"
        else
            echo "  ❌ 后端: 未运行"
        fi
        if curl -s http://localhost:5174 > /dev/null; then
            echo "  ✅ 前端: 运行中 (http://localhost:5174)"
        else
            echo "  ❌ 前端: 未运行"
        fi
        ;;
    stop)
        echo ""
        echo "🛑 停止所有服务..."
        pkill -f "uvicorn main:app" 2>/dev/null
        pkill -f "http.server 5174" 2>/dev/null
        echo "  ✅ 已停止"
        ;;
    restart)
        $0 stop
        sleep 1
        $0 all
        ;;
    *)
        echo "用法: $0 {backend|frontend|all|status|stop|restart}"
        echo ""
        echo "命令:"
        echo "  backend   - 只启动后端服务"
        echo "  frontend  - 只启动前端服务"
        echo "  all       - 启动所有服务 (默认)"
        echo "  status    - 查看服务状态"
        echo "  stop      - 停止所有服务"
        echo "  restart   - 重启所有服务"
        exit 1
esac

echo ""
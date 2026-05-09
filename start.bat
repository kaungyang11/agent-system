@echo off
chcp 65001 >nul
REM 代理商销售管理系统 - 一键启动脚本 (Windows)

echo =================================================================
echo                  🚀 代理商销售管理系统启动中...
echo =================================================================

REM 检查是否在backend目录
if not exist main.py (
    echo ❌ 请在 agent-system\backend 目录下运行此脚本
    pause
    exit /b 1
)

REM 检查并创建虚拟环境
if not exist "..\venv" (
    echo 📦 正在创建虚拟环境...
    cd ..
    python -m venv venv
    cd backend
    echo 📦 安装后端依赖...
    call ..\venv\Scripts\pip install -q -r requirements.txt
) else (
    echo 📦 安装后端依赖...
    call ..\venv\Scripts\pip install -q -r requirements.txt
)

REM 启动后端
echo 🚀 启动后端服务...
start "Backend" cmd /c "..\venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8000"
echo ✅ 后端已启动 (http://localhost:8000)

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 切换到前端目录启动
echo 🎨 启动前端服务...
cd /d "%~dp0..\frontend"

REM 检查是否安装了依赖
if not exist "node_modules" (
    echo 📦 正在安装前端依赖...
    call npm install
)

start "Frontend" cmd /c "npm run dev"
echo ✅ 前端已启动 (http://localhost:5173)

echo.
echo =================================================================
echo                         🎉 启动完成！
echo.
echo 📝 后端: http://localhost:8000
echo 📝 前端: http://localhost:5173
echo.
echo 🛑 停止服务: 关闭这两个CMD窗口
echo =================================================================
echo.
pause
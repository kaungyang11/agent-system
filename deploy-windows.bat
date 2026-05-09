@echo off
chcp 65001 >nul
echo ==========================================
echo   代理商销售系统 - Windows启动脚本
echo ==========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装
    echo 请从 https://python.org 下载安装 Python 3.10+
    echo 安装时务必勾选 "Add Python to PATH"
    pause
    exit /b 1
)

echo ✅ Python 已安装

REM 检查后端目录
if not exist "backend\main.py" (
    echo ❌ 后端文件不存在: backend\main.py
    echo 请确保从SophCLAW复制了backend目录
    pause
    exit /b 1
)

echo.
echo 【1】启动后端服务 (端口 8000)...
echo    API文档: http://localhost:8000/docs
start "代理商销售系统 - 后端" cmd /c "cd /d %~dp0backend && venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 检查后端是否启动
curl -s http://localhost:8000/api/health >nul
if errorlevel 1 (
    echo ❌ 后端启动失败
    pause
    exit /b 1
)
echo ✅ 后端启动成功

echo.
echo 【2】启动前端服务 (端口 5174)...
echo    前端页面: http://localhost:5174
start "代理商销售系统 - 前端" cmd /c "cd /d %~dp0frontend\dist && python -m http.server 5174"

timeout /t 2 /nobreak >nul

REM 检查前端是否启动
curl -s http://localhost:5174 >nul
if errorlevel 1 (
    echo ⚠️ 前端启动失败，但后端正常运行
) else (
    echo ✅ 前端启动成功
)

echo.
echo ==========================================
echo   ✅ 服务启动完成！
echo ==========================================
echo.
echo 访问地址:
echo   - 前端页面: http://localhost:5174
echo   - 后端API文档: http://localhost:8000/docs
echo.
echo 测试账号:
echo   - 管理员: admin / admin123
echo   - 销售: sales1 / sales123
echo   - 代理商: agent1 / agent123
echo   - 客户: customer1 / cust123
echo.
echo 按任意键退出...
pause >nul
# WSL 本地部署指南

## 简介

WSL (Windows Subsystem for Linux) 让你在Windows上运行Linux环境，非常适合部署Python应用。

## 前置准备

### 1. 启用WSL

以**管理员身份**打开PowerShell：

```powershell
# 启用WSL功能
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# 启用虚拟机平台
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 重启电脑
Restart-Computer
```

### 2. 安装WSL

```powershell
# 安装Ubuntu (推荐)
wsl --install -d Ubuntu
```

### 3. 打开WSL

```cmd
# 在Windows终端或命令提示符中
wsl
```

---

## 部署步骤

### 方法一：复制文件部署

#### 步骤1：准备文件

从SophCLAW下载以下文件到Windows：
- `agent-system-full.tar.gz`

#### 步骤2：复制到WSL

```cmd
# 在Windows命令提示符中
wsl mkdir -p ~/agent-system
wsl --cpython "C:\下载目录\agent-system-full.tar.gz" ~/agent-system/
```

或者直接在WSL中操作：

```bash
# 进入WSL后
cd ~
mkdir -p agent-system/backend
mkdir -p agent-system/frontend/dist

# 将文件从Windows复制到WSL
cp /mnt/c/下载目录/agent-system-full.tar.gz ~/
cd ~/agent-system
tar -xzf ../agent-system-full.tar.gz
```

#### 步骤3：安装依赖

```bash
cd ~/agent-system/backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt -q
```

#### 步骤4：启动服务

```bash
# 终端1: 启动后端
cd ~/agent-system/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# 终端2: 启动前端
cd ~/agent-system/frontend/dist
python3 -m http.server 5174
```

#### 步骤5：访问测试

在Windows浏览器中打开：
- http://localhost:5174 (前端)
- http://localhost:8000/docs (API文档)

---

### 方法二：Git克隆部署

如果你的Windows可以访问SophCLAW仓库：

```bash
# 在WSL中
cd ~
git clone <your-repo-url> agent-system
cd agent-system/backend

# 安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt -q

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 快速启动脚本

### 创建一键启动脚本

```bash
# 在WSL中
cd ~/agent-system

# 创建启动脚本
cat > start.sh << 'EOF'
#!/bin/bash
cd ~/agent-system/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
echo "后端已启动 (PID: $!)"

cd ~/agent-system/frontend/dist
nohup python3 -m http.server 5174 --bind 0.0.0.0 > /tmp/frontend.log 2>&1 &
echo "前端已启动 (PID: $!)"

echo ""
echo "服务已启动:"
echo "  前端: http://localhost:5174"
echo "  后端: http://localhost:8000/docs"
EOF

chmod +x start.sh
```

### 使用

```bash
# 启动服务
./start.sh

# 停止服务
pkill -f "uvicorn main:app"
pkill -f "http.server 5174"
```

---

## 常见问题

### Q1: WSL中Python版本过旧

```bash
# 检查版本
python3 --version

# 如需升级
sudo apt update
sudo apt install python3.11
```

### Q2: 端口无法访问

```bash
# 检查防火墙 (Windows)
Windows Defender 防火墙 → 允许应用通过防火墙

# 或在WSL中检查
curl http://localhost:8000/api/health
```

### Q3: 文件权限问题

```bash
# 修复权限
chmod -R 755 ~/agent-system
```

### Q4: 从Windows访问WSL服务

WSL2默认使用虚拟IP，可能需要：
```powershell
# 查看WSL IP
wsl hostname -I
```

然后使用该IP访问：
```
http://<WSL-IP>:5174
```

---

## 服务管理

### 启动服务

```bash
# 方式1: 分别启动
# 终端1
cd ~/agent-system/backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# 终端2
cd ~/agent-system/frontend/dist
python3 -m http.server 5174
```

### 停止服务

```bash
# 查找进程
ps aux | grep uvicorn
ps aux | grep "http.server"

# 终止进程
kill <PID>
```

### 设置开机自启

在Windows任务计划程序中设置WSL启动时运行脚本。

---

## 测试验证

```bash
# 健康检查
curl http://localhost:8000/api/health

# 产品列表
curl http://localhost:8000/api/v1/products

# 代理商列表
curl http://localhost:8000/api/v1/agents
```

---

## 文件结构

```
~/agent-system/
├── backend/
│   ├── main.py              # 后端入口
│   ├── data.db              # 数据库
│   ├── requirements.txt     # Python依赖
│   ├── app/                 # 后端代码
│   └── venv/                # Python虚拟环境
│
├── frontend/
│   └── dist/                # 前端静态文件
│       ├── index.html
│       └── assets/
│
└── start.sh                 # 启动脚本
```
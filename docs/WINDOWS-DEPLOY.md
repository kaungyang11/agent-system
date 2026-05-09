# Windows 本地部署指南

## 前置准备

### 1. 下载所需文件

从SophCLAW下载以下文件到Windows本地目录 `C:\AgentSystem\`：

```
C:\AgentSystem\
├── backend/
│   ├── data.db              (数据库文件，约70KB)
│   ├── main.py              (后端入口)
│   ├── requirements.txt     (依赖列表)
│   └── app/                 (后端源代码)
│       ├── database.py
│       ├── models/
│       ├── routers/
│       ├── schemas/
│       └── __init__.py
│
└── frontend/                (可选，前端UI)
    └── dist/
        ├── index.html
        └── assets/
```

**下载方法**：
- 在SophCLAW文件管理器中找到 `workspace-dai_li_shang_xiao_shou_xi_tong/`
- 打包下载 `backend/` 和 `frontend/dist/`
- 或使用命令行打包后下载

### 2. 安装Python

1. 访问 https://www.python.org/downloads/
2. 下载 **Python 3.10 或 3.11**
3. 运行安装程序
4. **⚠️ 重要**: 勾选 "Add Python to PATH"
5. 点击 "Install Now"

验证安装：
```cmd
python --version
# 应该显示: Python 3.10.x 或 3.11.x
```

---

## 安装步骤

### 步骤1：打开命令提示符

按 `Win + R`，输入 `cmd`，回车

### 步骤2：进入后端目录

```cmd
cd C:\AgentSystem\backend
```

### 步骤3：创建虚拟环境

```cmd
python -m venv venv
```

### 步骤4：激活虚拟环境

```cmd
venv\Scripts\activate
```

激活成功会显示 `(venv)` 前缀

### 步骤5：安装依赖

```cmd
pip install -r requirements.txt -q
```

等待安装完成...

### 步骤6：启动后端服务

```cmd
uvicorn main:app --host 0.0.0.0 --port 8000
```

看到以下输出说明启动成功：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 步骤7：启动前端（可选）

打开**新的**命令提示符窗口：

```cmd
cd C:\AgentSystem\frontend\dist
python -m http.server 5174
```

看到以下输出说明启动成功：
```
Serving HTTP on 0.0.0.0 port 5174 (http://0.0.0.0:5174/)
```

---

## 访问测试

打开浏览器访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端页面 | http://localhost:5174 | 登录界面 |
| 后端API文档 | http://localhost:8000/docs | Swagger文档 |
| API根路径 | http://localhost:8000 | 健康检查 |

### 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 销售 | sales1 | sales123 |
| 代理商 | agent1 | agent123 |
| 客户 | customer1 | cust123 |

---

## 快速验证

### 1. API健康检查

```cmd
curl http://localhost:8000/api/health
# 应该返回: {"status":"ok","message":"服务运行正常"}
```

### 2. 登录获取Token

```cmd
curl -X POST http://localhost:8000/api/v1/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

### 3. 查看产品列表

```cmd
curl http://localhost:8000/api/v1/products
```

---

## 常见问题

### Q1: 端口被占用

```cmd
# 查找占用端口的进程
netstat -ano | findstr :8000

# 终止进程 (需要管理员权限)
taskkill /PID <PID号> /F
```

### Q2: pip安装失败

```cmd
# 升级pip
python -m pip install --upgrade pip

# 重新安装
pip install -r requirements.txt
```

### Q3: 无法连接数据库

确保 `data.db` 文件与 `main.py` 在同一目录

### Q4: 中文显示乱码

在cmd中执行：
```cmd
chcp 65001
```

---

## 使用完成后关闭服务

在运行后端和前端的命令提示符窗口中按 `Ctrl + C`

---

## 文件打包下载（可选）

如果需要从SophCLAW下载整个项目：

```bash
# 在SophCLAW终端中打包
cd /home/node/.openclaw/workspace-dai_li_shang_xiao_shou_xi_tong
tar -czvf agent-system-windows.tar.gz \
  backend/data.db \
  backend/main.py \
  backend/requirements.txt \
  backend/app/ \
  frontend/dist/
```

然后在SophCLAW文件管理器中下载 `agent-system-windows.tar.gz`

解压到Windows后，按上述步骤运行即可。
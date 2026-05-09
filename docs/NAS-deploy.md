# NAS 部署方案

## 方案对比

| 方案 | 难度 | 稳定性 | 适用场景 |
|------|------|--------|----------|
| **A. Docker部署** | ⭐⭐ | ⭐⭐⭐⭐⭐ | 专业NAS(QNAP/Synology) |
| **B. 直接部署** | ⭐ | ⭐⭐⭐⭐ | 所有NAS/服务器 |
| **C. Python部署** | ⭐ | ⭐⭐⭐ | 轻量使用 |

---

## 方案A: Docker 部署 (推荐)

### 1. 准备文件

```
/share/AgentSystem/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ...
├── frontend/
│   └── dist/ (构建后的静态文件)
└── data/ (数据库存储)
```

### 2. docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  frontend:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
    restart: unless-stopped

  # 可选: Nginx反向代理(统一入口)
  proxy:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./nginx-proxy.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
```

### 3. Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. Nginx 配置 (前端+API代理)

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # 前端路由
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API 代理到后端
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 5. 启动命令

```bash
# 构建并启动
docker-compose up -d --build

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

---

## 方案B: 直接部署 (简单)

适合NAS上有Python环境的情况

### 1. 上传文件到NAS

```bash
# 在NAS上创建目录
mkdir -p /share/AgentSystem/backend
mkdir -p /share/AgentSystem/frontend

# 上传文件 (使用Samba/SCP/File Station)
# 上传 backend/ 目录内容到 /share/AgentSystem/backend/
# 上传 frontend/dist/ 目录内容到 /share/AgentSystem/frontend/
```

### 2. 安装依赖

```bash
cd /share/AgentSystem/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 启动服务

**创建启动脚本** `/share/AgentSystem/start.sh`:

```bash
#!/bin/bash
cd /share/AgentSystem

# 启动后端 (端口 8000)
cd backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &

# 启动前端 (端口 80/8080)
cd ../frontend
nohup python3 -m http.server 8080 --bind 0.0.0.0 > ../frontend.log 2>&1 &

echo "服务已启动"
echo "前端: http://NAS_IP:8080"
echo "后端: http://NAS_IP:8000"
```

**设置开机自启**:

```bash
# 添加到NAS的开机启动脚本
# 或使用 crontab
@reboot /share/AgentSystem/start.sh
```

### 4. 访问地址

- 前端: `http://<NAS_IP>:8080`
- 后端API: `http://<NAS_IP>:8000/docs`

---

## 方案C: Python http.server (最简)

仅需上传前端静态文件

### 1. 上传前端文件

```
/share/AgentSystem/
└── dist/ (frontend/dist的全部内容)
```

### 2. 启动服务

```bash
cd /share/AgentSystem/dist
nohup python3 -m http.server 8080 --bind 0.0.0.0 &
```

### ⚠️ 注意

此方案前端和API分开，需要确保后端API地址可访问。

---

## 数据备份策略

### 备份内容

```
/share/AgentSystem/
├── data/           # 数据库 (data.db)
├── backend/logs/   # 日志文件
└── frontend/       # 前端文件
```

### 备份脚本

```bash
#!/bin/bash
BACKUP_DIR="/share/Backup/AgentSystem"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp /share/AgentSystem/backend/data.db $BACKUP_DIR/data_$DATE.db

# 打包全部
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz /share/AgentSystem

echo "备份完成: backup_$DATE.tar.gz"
```

### 自动备份 (crontab)

```bash
# 每天凌晨2点自动备份
0 2 * * * /share/AgentSystem/backup.sh
```

---

## 端口映射 (外网访问)

### 方案1: NAS端口转发

| 服务 | 内网端口 | 外网端口 |
|------|----------|----------|
| 前端 | 8080 | 80/443 |
| 后端 | 8000 | 8000 |

### 方案2: VPN + 内网访问

1. 配置NAS VPN服务
2. 员工连接VPN后访问内网地址
3. 更安全

### 方案3: 内网穿透 (frp/花生壳)

```bash
# frpc.ini
[agent-system]
type = tcp
local_ip = 127.0.0.1
local_port = 8080
remote_port = 6000
```

---

## 访问地址总结

| 环境 | 前端地址 | API地址 |
|------|----------|---------|
| 本地开发 | localhost:5174 | localhost:8000 |
| NAS直接 | NAS_IP:8080 | NAS_IP:8000 |
| Docker | NAS_IP:80 | NAS_IP:8000 |

---

## 快速部署 checklist

- [ ] 文件上传到NAS
- [ ] 安装Python依赖
- [ ] 配置启动脚本
- [ ] 设置开机自启
- [ ] 配置端口映射
- [ ] 测试访问
- [ ] 配置备份策略
# SophCLAW 访问指南

## 问题说明

SophCLAW 内置浏览器是隔离环境，无法直接访问 `localhost:5174` 或 `localhost:8000`

## 解决方案

### 方法1：使用 SophCLAW Canvas/浏览器功能

1. 在 SophCLAW 界面中找到 **Canvas** 或 **浏览器** 按钮
2. 点击后选择或输入：
   - 路径: `/canvas/frontend/`
   - 或选择 `canvas/frontend` 目录

### 方法2：通过网关静态托管

SophCLAW 通常提供静态文件托管服务，访问地址可能是：

```
http://localhost:18789/canvas/frontend/
```

或者

```
http://localhost:18789/<workspace-name>/canvas/frontend/
```

### 方法3：使用浏览器工具

如果SophCLAW界面有"浏览器"按钮，可以直接打开并输入前端访问地址。

## 当前文件位置

```
/home/node/.openclaw/workspace-dai_li_shang_xiao_shou_xi_tong/canvas/frontend/
├── index.html          # 前端入口
├── assets/             # 静态资源
└── ...

/home/node/.openclaw/workspace-dai_li_shang_xiao_shou_xi_tong/backend/
└── data.db             # SQLite数据库
```

## 前端访问方式

前端文件已复制到 `canvas/frontend/` 目录，请尝试以下方式访问：

1. **通过SophCLAW界面**: 寻找浏览器/Canvas图标
2. **输入路径**: `/canvas/frontend/index.html`
3. **使用网关**: `http://localhost:18789/canvas/frontend/`

## 备选方案：如果仍然无法访问

可以使用 SophCLAW 的 **Shell/终端** 功能进行命令行测试：

```bash
# 1. 登录获取Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 2. 查看产品列表
curl -X GET http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer <your-token>"

# 3. 创建订单
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "agent_id": 1, "product_id": 1, "quantity": 5, "unit_price": 1100}'
```

## 端口说明

| 服务 | 端口 | 说明 |
|------|------|------|
| 前端(静态) | 5174 | 浏览器无法直接访问 |
| 后端API | 8000 | 浏览器无法直接访问 |
| SophCLAW网关 | 18789 | SophCLAW控制界面 |

## 联系管理员

如果以上方法都无法访问，请联系系统管理员：
1. 确认SophCLAW网关配置
2. 确认静态文件托管路径
3. 配置API代理规则
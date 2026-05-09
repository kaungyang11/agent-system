# 本地测试指南

## 方式一：直接使用当前环境

### 访问地址
| 服务 | 地址 | 说明 |
|------|------|------|
| 前端页面 | http://localhost:5174 | 浏览器打开 |
| 后端API文档 | http://localhost:8000/docs | Swagger UI |
| API基础地址 | http://localhost:8000/api/v1 | - |

### 测试账号
| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 销售 | sales1 | sales123 |
| 代理商 | agent1 | agent123 |
| 客户 | customer1 | cust123 |

---

## 方式二：命令行测试 (cURL)

### 1. 启动服务（如果未运行）

```bash
cd /home/node/.openclaw/workspace-dai_li_shang_xiao_shou_xi_tong

# 启动后端
cd backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &

# 启动前端
cd ../frontend/dist
nohup python3 -m http.server 5174 --bind 0.0.0.0 > /tmp/frontend.log 2>&1 &
```

### 2. 快速功能测试

```bash
# 获取管理员Token
ADMIN_TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 测试产品列表
curl -X GET http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# 测试创建订单
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "agent_id": 1, "product_id": 1, "quantity": 5, "unit_price": 1100}'
```

### 3. 一键测试脚本

创建 `test-api.sh`:

```bash
#!/bin/bash

# 获取Token
echo "=== 1. 登录获取Token ==="
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token: ${TOKEN:0:30}..."

echo ""
echo "=== 2. 测试产品列表 ==="
curl -s -X GET http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -20

echo ""
echo "=== 3. 测试代理商列表 ==="
curl -s -X GET http://localhost:8000/api/v1/agents \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -20

echo ""
echo "=== 4. 测试订单列表 ==="
curl -s -X GET http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | head -20

echo ""
echo "=== 测试完成! ==="
```

运行:
```bash
chmod +x test-api.sh
./test-api.sh
```

---

## 方式三：Postman/Apifox 测试

### 导入集合

创建一个新集合，添加以下请求:

#### 1. 登录
```
POST http://localhost:8000/api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```
**响应**: 保存返回的 `access_token`

#### 2. 获取用户信息
```
GET http://localhost:8000/api/v1/auth/me
Authorization: Bearer <your-token>
```

#### 3. 产品管理
```
GET    http://localhost:8000/api/v1/products
POST   http://localhost:8000/api/v1/products
PUT    http://localhost:8000/api/v1/products/1
DELETE http://localhost:8000/api/v1/products/1
```

#### 4. 订单管理
```
GET  http://localhost:8000/api/v1/orders
POST http://localhost:8000/api/v1/orders
```

**POST Body 示例**:
```json
{
  "customer_id": 1,
  "agent_id": 1,
  "product_id": 1,
  "quantity": 5,
  "unit_price": 1100
}
```

#### 5. 业绩管理
```
GET  http://localhost:8000/api/v1/performance
POST http://localhost:8000/api/v1/performance

PUT  http://localhost:8000/api/v1/performance/1/approve
Body: {"approved": true}

POST http://localhost:8000/api/v1/performance/1/settle
Body: {"settled": true}
```

---

## 方式四：前端UI测试

### 访问前端页面

1. 打开浏览器访问: **http://localhost:5174**
2. 使用测试账号登录:
   - 用户名: `admin`
   - 密码: `admin123`

### 测试流程

```
1. 登录 → 进入首页
2. 产品管理 → 查看/添加产品
3. 代理商管理 → 查看代理商余额
4. 库存管理 → 备货入库
5. 客户管理 → 添加客户
6. 订单管理 → 下单
7. 业绩管理 → 提交/审核业绩
```

---

## 方式五：完整业务流程测试

### 场景：代理商下单流程

```bash
# 0. 获取管理员Token
ADMIN_TOKEN="eyJhbGciOiJIUzI1NiIs..."

# 1. 代理商备货 (agent1采购10台)
echo "=== 1. 代理商备货 ==="
curl -X POST http://localhost:8000/api/v1/inventory \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": 1, "product_id": 1, "quantity": 10}'

# 2. 创建订单 (客户下单5台)
echo -e "\n=== 2. 创建订单 ==="
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"customer_id": 1, "agent_id": 1, "product_id": 1, "quantity": 5, "unit_price": 1100}'

# 3. 订单状态流转
echo -e "\n=== 3. 订单发货 ==="
curl -X PUT http://localhost:8000/api/v1/orders/8/status \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "shipped"}'

# 4. 提交业绩
echo -e "\n=== 4. 提交业绩 ==="
curl -X POST http://localhost:8000/api/v1/performance \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"order_id": 8, "sales_id": 2, "agent_id": 1, "customer_id": 1, "product_id": 1, "quantity": 5, "lp_price": 1000, "pdc_price": 1100, "reward_amount": 50}'

# 5. 审核业绩
echo -e "\n=== 5. 审核业绩 ==="
curl -X PUT http://localhost:8000/api/v1/performance/5/approve \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"approved": true}'

# 6. 发放奖励
echo -e "\n=== 6. 发放奖励 ==="
curl -X POST "http://localhost:8000/api/v1/performance/5/settle" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"settled": true}'

# 7. 查看余额变化
echo -e "\n=== 7. 查看余额 ==="
curl -X GET "http://localhost:8000/api/v1/agents/1/balance" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 故障排查

### 端口被占用
```bash
# 查看占用端口的进程
lsof -i:8000
lsof -i:5174

# 停止进程
kill <PID>
```

### 服务未启动
```bash
# 手动启动后端
cd backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000

# 手动启动前端
cd frontend/dist
python3 -m http.server 5174
```

### Token无效
```bash
# 重新登录获取新Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

---

## 测试检查清单

- [ ] 后端服务运行 (端口8000)
- [ ] 前端服务运行 (端口5174)
- [ ] 可以登录
- [ ] 可以查看产品列表
- [ ] 可以创建订单
- [ ] 订单状态可以更新
- [ ] 可以提交业绩
- [ ] 可以审核业绩
- [ ] 代理商余额正确增加
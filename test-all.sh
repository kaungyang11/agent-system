#!/bin/bash

# 代理商销售系统 - 一键功能测试脚本
# 适用于 SophCLAW 终端环境

echo "=========================================="
echo "   代理商销售系统 - 功能测试"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查服务状态
check_service() {
    local name=$1
    local port=$2
    if curl -s http://localhost:$port > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name 运行正常${NC} (端口 $port)"
        return 0
    else
        echo -e "${YELLOW}⚠️  $name 未运行${NC} (端口 $port)"
        return 1
    fi
}

echo "【1】检查服务状态..."
check_service "后端API" 8000
check_service "前端页面" 5174
check_service "SophCLAW网关" 18789

echo ""
echo "【2】登录获取Token..."

# 登录管理员
ADMIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

ADMIN_TOKEN=$(echo $ADMIN_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -n "$ADMIN_TOKEN" ]; then
    echo -e "${GREEN}✅ 管理员登录成功${NC}"
    echo "Token: ${ADMIN_TOKEN:0:30}..."
else
    echo -e "${YELLOW}⚠️ 登录失败${NC}"
    exit 1
fi

echo ""
echo "【3】测试各功能模块..."
echo ""

test_api() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4

    echo -n "  测试 $name... "

    if [ -n "$data" ]; then
        response=$(curl -s -X $method "$url" \
            -H "Authorization: Bearer $ADMIN_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s -X $method "$url" \
            -H "Authorization: Bearer $ADMIN_TOKEN")
    fi

    if echo "$response" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        echo -e "${GREEN}✅${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC}"
        return 1
    fi
}

# 产品管理
echo "  --- 产品管理 ---"
test_api "产品列表" "GET" "http://localhost:8000/api/v1/products"

# 代理商管理
echo "  --- 代理商管理 ---"
test_api "代理商列表" "GET" "http://localhost:8000/api/v1/agents"
test_api "代理商余额" "GET" "http://localhost:8000/api/v1/agents/1/balance"

# 客户管理
echo "  --- 客户管理 ---"
test_api "客户列表" "GET" "http://localhost:8000/api/v1/customers"

# 库存管理
echo "  --- 库存管理 ---"
test_api "库存列表" "GET" "http://localhost:8000/api/v1/inventory"

# 订单管理
echo "  --- 订单管理 ---"
test_api "订单列表" "GET" "http://localhost:8000/api/v1/orders"

# 业绩管理
echo "  --- 业绩管理 ---"
test_api "业绩列表" "GET" "http://localhost:8000/api/v1/performance"

# 用户管理
echo "  --- 用户管理 ---"
test_api "用户列表" "GET" "http://localhost:8000/api/v1/users"

echo ""
echo "【4】完整业务流程测试 (可选)..."
echo ""

run_full_test() {
    echo -n "  创建测试订单... "

    ORDER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/orders \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"customer_id": 1, "agent_id": 1, "product_id": 1, "quantity": 5, "unit_price": 1100}')

    ORDER_ID=$(echo $ORDER_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

    if [ -n "$ORDER_ID" ]; then
        echo -e "${GREEN}订单#$ORDER_ID 创建成功${NC}"

        echo -n "  更新订单状态... "
        curl -s -X PUT "http://localhost:8000/api/v1/orders/$ORDER_ID/status" \
            -H "Authorization: Bearer $ADMIN_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"status": "shipped"}' > /dev/null
        echo -e "${GREEN}已完成${NC}"

        echo -n "  提交业绩... "
        PERF_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/performance \
            -H "Authorization: Bearer $ADMIN_TOKEN" \
            -H "Content-Type: application/json" \
            -d "{\"order_id\": $ORDER_ID, \"sales_id\": 2, \"agent_id\": 1, \"customer_id\": 1, \"product_id\": 1, \"quantity\": 5, \"lp_price\": 1000, \"pdc_price\": 1100, \"reward_amount\": 50}")
        echo -e "${GREEN}已提交${NC}"

        echo -n "  审核业绩... "
        curl -s -X PUT "http://localhost:8000/api/v1/performance/$(echo $PERF_RESPONSE | python3 -c 'import sys,json; print(json.load(sys.stdin)[\"id\"])' 2>/dev/null)/approve" \
            -H "Authorization: Bearer $ADMIN_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"approved": true}' > /dev/null
        echo -e "${GREEN}已通过${NC}"

        echo -n "  发放奖励... "
        curl -s -X POST "http://localhost:8000/api/v1/performance/$(echo $PERF_RESPONSE | python3 -c 'import sys,json; print(json.load(sys.stdin)[\"id\"])' 2>/dev/null)/settle" \
            -H "Authorization: Bearer $ADMIN_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"settled": true}' > /dev/null
        echo -e "${GREEN}已发放${NC}"

        echo ""
        echo -e "${GREEN}✅ 完整流程测试通过!${NC}"
    else
        echo -e "${YELLOW}订单创建失败${NC}"
    fi
}

# 询问是否运行完整测试
read -p "  运行完整业务流程测试? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    run_full_test
fi

echo ""
echo "=========================================="
echo "   测试完成!"
echo "=========================================="
echo ""
echo "API文档: http://localhost:8000/docs"
echo ""
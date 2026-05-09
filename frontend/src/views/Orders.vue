<template>
  <div class="page-container">
    <div class="page-header">
      <h2>订单管理</h2>
      <el-button type="primary" @click="showDialog">下单</el-button>
    </div>

    <el-table :data="orders" stripe style="width: 100%">
      <el-table-column prop="order_no" label="订单号" width="150" />
      <el-table-column prop="customer_name" label="客户" />
      <el-table-column prop="agent_name" label="代理商" width="150" />
      <el-table-column prop="product_name" label="产品" />
      <el-table-column prop="quantity" label="数量" width="80" />
      <el-table-column prop="price" label="价格" width="100">
        <template #default="{ row }">
          ¥{{ row.price?.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="agent_balance" label="代理商余额" width="120">
        <template #default="{ row }">
          <span :class="{ 'text-danger': row.agent_balance < 1000 }">
            ¥{{ row.agent_balance?.toFixed(2) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="product_stock" label="产品库存" width="100">
        <template #default="{ row }">
          <span :class="{ 'text-danger': row.product_stock < 10 }">
            {{ row.product_stock }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-select 
            v-model="row.status" 
            size="small" 
            @change="updateStatus(row)"
            style="width: 100px"
          >
            <el-option label="待处理" value="pending" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="下单" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="客户">
          <el-select v-model="form.customer_id" placeholder="选择客户" filterable style="width: 100%">
            <el-option 
              v-for="c in customers" 
              :key="c.id" 
              :label="c.name" 
              :value="c.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="代理商">
          <el-select v-model="form.agent_id" placeholder="选择代理商" filterable style="width: 100%" @change="onAgentChange">
            <el-option 
              v-for="a in agents" 
              :key="a.id" 
              :label="a.name" 
              :value="a.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="产品">
          <el-select v-model="form.product_id" placeholder="选择产品" filterable @change="onProductChange" style="width: 100%">
            <el-option 
              v-for="p in products" 
              :key="p.id" 
              :label="p.name + ' (库存:' + getProductStock(p.id) + ')'" 
              :value="p.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="form.quantity" :min="1" :max="maxQuantity" @change="calculatePrice" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单价">
          <el-input-number v-model="form.unit_price" :precision="2" :min="0" @change="calculatePrice" style="width: 100%" />
        </el-form-item>
        <el-form-item label="总价">
          <span style="font-size: 20px; color: #f56c6c; font-weight: bold;">¥{{ form.total_price?.toFixed(2) }}</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitOrder">提交订单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const orders = ref([])
const customers = ref([])
const products = ref([])
const agents = ref([])
const inventory = ref([])
const dialogVisible = ref(false)
const form = ref({
  customer_id: null,
  agent_id: null,
  product_id: null,
  quantity: 1,
  unit_price: 0,
  total_price: 0
})

const maxQuantity = computed(() => {
  if (!form.value.agent_id || !form.value.product_id) return 999
  const inv = inventory.value.find(i => i.agent_id === form.value.agent_id && i.product_id === form.value.product_id)
  return inv ? inv.quantity : 999
})

const getProductStock = (productId) => {
  if (!form.value.agent_id) return 0
  const inv = inventory.value.find(i => i.agent_id === form.value.agent_id && i.product_id === productId)
  return inv ? inv.quantity : 0
}

const fetchOrders = async () => {
  try {
    orders.value = await api.getOrders()
  } catch (error) {
    ElMessage.error('获取订单列表失败')
  }
}

const fetchCustomers = async () => {
  try {
    customers.value = await api.getCustomers()
  } catch (error) {
    console.error('获取客户列表失败')
  }
}

const fetchProducts = async () => {
  try {
    products.value = await api.getProducts()
  } catch (error) {
    console.error('获取产品列表失败')
  }
}

const fetchAgents = async () => {
  try {
    agents.value = await api.getAgents()
  } catch (error) {
    console.error('获取代理商列表失败')
  }
}

const fetchInventory = async () => {
  try {
    inventory.value = await api.getInventory()
  } catch (error) {
    console.error('获取库存列表失败')
  }
}

const showDialog = () => {
  form.value = { customer_id: null, agent_id: null, product_id: null, quantity: 1, unit_price: 0, total_price: 0 }
  dialogVisible.value = true
}

const onAgentChange = () => {
  calculatePrice()
}

const onProductChange = (productId) => {
  const product = products.value.find(p => p.id === productId)
  if (product) {
    form.value.unit_price = product.lp_price || 0
    calculatePrice()
  }
}

const calculatePrice = () => {
  form.value.total_price = (form.value.quantity || 0) * (form.value.unit_price || 0)
}

const submitOrder = async () => {
  if (!form.value.customer_id || !form.value.agent_id || !form.value.product_id) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    await api.createOrder({
      customer_id: form.value.customer_id,
      agent_id: form.value.agent_id,
      product_id: form.value.product_id,
      quantity: form.value.quantity,
      unit_price: form.value.unit_price
    })
    ElMessage.success('下单成功')
    dialogVisible.value = false
    fetchOrders()
    fetchInventory()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '下单失败')
  }
}

const updateStatus = async (order) => {
  try {
    await api.updateOrder(order.id, { status: order.status })
    ElMessage.success('状态更新成功')
    fetchInventory()
  } catch (error) {
    ElMessage.error('状态更新失败')
    fetchOrders()
  }
}

const getStatusType = (status) => {
  const types = { pending: 'warning', shipped: 'primary', completed: 'success', cancelled: 'danger' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { pending: '待处理', shipped: '已发货', completed: '已完成', cancelled: '已取消' }
  return texts[status] || status
}

onMounted(() => {
  fetchOrders()
  fetchCustomers()
  fetchProducts()
  fetchAgents()
  fetchInventory()
})
</script>

<style scoped>
.page-container {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.page-header h2 {
  font-size: 18px;
  color: #303133;
}
.text-danger {
  color: #f56c6c;
  font-weight: bold;
}
</style>
<template>
  <div class="page-container">
    <div class="page-header">
      <h2>库存管理</h2>
      <el-button type="primary" @click="showStockInDialog">备货入库</el-button>
    </div>

    <el-table :data="inventory" stripe style="width: 100%">
      <el-table-column prop="agent_name" label="代理商" />
      <el-table-column prop="product_name" label="产品" />
      <el-table-column prop="product_code" label="产品编码" width="150" />
      <el-table-column prop="quantity" label="库存数量" width="120">
        <template #default="{ row }">
          <span :style="{ color: row.quantity < 10 ? '#f56c6c' : '#67c23a' }">
            {{ row.quantity }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="更新时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="viewDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="stockInVisible" title="备货入库" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="代理商">
          <el-select v-model="form.agent_id" placeholder="选择代理商" filterable>
            <el-option 
              v-for="a in agents" 
              :key="a.id" 
              :label="a.name" 
              :value="a.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="产品">
          <el-select v-model="form.product_id" placeholder="选择产品" filterable>
            <el-option 
              v-for="p in products" 
              :key="p.id" 
              :label="p.name" 
              :value="p.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="入库数量">
          <el-input-number v-model="form.quantity" :min="1" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="stockInVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStockIn">确认入库</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="库存详情" width="500px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="代理商">{{ currentItem?.agent_name }}</el-descriptions-item>
        <el-descriptions-item label="产品">{{ currentItem?.product_name }}</el-descriptions-item>
        <el-descriptions-item label="产品编码">{{ currentItem?.product_code }}</el-descriptions-item>
        <el-descriptions-item label="库存数量">
          <span style="font-weight: bold;">{{ currentItem?.quantity }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="最后更新">{{ currentItem?.updated_at }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const inventory = ref([])
const agents = ref([])
const products = ref([])
const stockInVisible = ref(false)
const detailVisible = ref(false)
const currentItem = ref(null)
const form = ref({
  agent_id: null,
  product_id: null,
  quantity: 1,
  remark: ''
})

const fetchInventory = async () => {
  try {
    inventory.value = await api.getInventory()
  } catch (error) {
    ElMessage.error('获取库存列表失败')
  }
}

const fetchAgents = async () => {
  try {
    agents.value = await api.getAgents()
  } catch (error) {
    console.error('获取代理商列表失败')
  }
}

const fetchProducts = async () => {
  try {
    products.value = await api.getProducts()
  } catch (error) {
    console.error('获取产品列表失败')
  }
}

const showStockInDialog = () => {
  form.value = { agent_id: null, product_id: null, quantity: 1, remark: '' }
  stockInVisible.value = true
}

const submitStockIn = async () => {
  try {
    await api.createInventory(form.value)
    ElMessage.success('入库成功')
    stockInVisible.value = false
    fetchInventory()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '入库失败')
  }
}

const viewDetail = (row) => {
  currentItem.value = row
  detailVisible.value = true
}

onMounted(() => {
  fetchInventory()
  fetchAgents()
  fetchProducts()
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
</style>
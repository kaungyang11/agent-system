<template>
  <div class="page-container">
    <div class="page-header">
      <h2>业绩管理</h2>
      <el-button type="primary" @click="showDialog">提交业绩</el-button>
    </div>

    <el-table :data="performanceList" stripe style="width: 100%">
      <el-table-column prop="order_no" label="订单号" width="180" />
      <el-table-column prop="agent_name" label="代理商" />
      <el-table-column prop="customer_name" label="客户" />
      <el-table-column prop="amount" label="业绩金额" width="120">
        <template #default="{ row }">
          <span style="color: #f56c6c; font-weight: bold;">
            ¥{{ row.amount?.toFixed(2) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="submitted_at" label="提交时间" width="180" />
      <el-table-column prop="reviewed_at" label="审核时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="viewDetail(row)">查看</el-button>
          <template v-if="row.status === 'pending'">
            <el-button type="success" link @click="approve(row)">通过</el-button>
            <el-button type="danger" link @click="reject(row)">拒绝</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="提交业绩" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="订单号">
          <el-input v-model="form.order_no" placeholder="输入订单号" />
        </el-form-item>
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
        <el-form-item label="客户">
          <el-select v-model="form.customer_id" placeholder="选择客户" filterable>
            <el-option 
              v-for="c in customers" 
              :key="c.id" 
              :label="c.name" 
              :value="c.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="业绩金额">
          <el-input-number v-model="form.amount" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="合同">
          <el-upload
            action="#"
            :auto-upload="false"
            :on-change="(file) => handleFileChange(file, 'contract')"
            :limit="1"
          >
            <el-button type="primary">上传合同</el-button>
            <template #tip>
              <div class="el-upload__tip">支持 jpg/png/pdf 格式</div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="付款凭证">
          <el-upload
            action="#"
            :auto-upload="false"
            :on-change="(file) => handleFileChange(file, 'payment')"
            :limit="1"
          >
            <el-button type="primary">上传付款凭证</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="发货凭证">
          <el-upload
            action="#"
            :auto-upload="false"
            :on-change="(file) => handleFileChange(file, 'delivery')"
            :limit="1"
          >
            <el-button type="primary">上传发货凭证</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPerformance">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="业绩详情" width="700px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">{{ currentItem?.order_no }}</el-descriptions-item>
        <el-descriptions-item label="代理商">{{ currentItem?.agent_name }}</el-descriptions-item>
        <el-descriptions-item label="客户">{{ currentItem?.customer_name }}</el-descriptions-item>
        <el-descriptions-item label="业绩金额">
          <span style="color: #f56c6c; font-weight: bold;">
            ¥{{ currentItem?.amount?.toFixed(2) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentItem?.status)">
            {{ getStatusText(currentItem?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ currentItem?.submitted_at }}</el-descriptions-item>
        <el-descriptions-item label="审核时间">{{ currentItem?.reviewed_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="审核备注">{{ currentItem?.review_remark || '-' }}</el-descriptions-item>
      </el-descriptions>
      
      <div class="attachments" style="margin-top: 20px;">
        <h4>附件</h4>
        <div v-if="currentItem?.contract_url" class="attachment-item">
          <el-link :href="currentItem.contract_url" target="_blank">合同</el-link>
        </div>
        <div v-if="currentItem?.payment_url" class="attachment-item">
          <el-link :href="currentItem.payment_url" target="_blank">付款凭证</el-link>
        </div>
        <div v-if="currentItem?.delivery_url" class="attachment-item">
          <el-link :href="currentItem.delivery_url" target="_blank">发货凭证</el-link>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const performanceList = ref([])
const agents = ref([])
const customers = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const currentItem = ref(null)
const form = ref({
  order_no: '',
  agent_id: null,
  customer_id: null,
  amount: 0,
  contract: null,
  payment: null,
  delivery: null
})

const fetchPerformance = async () => {
  try {
    performanceList.value = await api.getPerformance()
  } catch (error) {
    ElMessage.error('获取业绩列表失败')
  }
}

const fetchAgents = async () => {
  try {
    agents.value = await api.getAgents()
  } catch (error) {
    console.error('获取代理商列表失败')
  }
}

const fetchCustomers = async () => {
  try {
    customers.value = await api.getCustomers()
  } catch (error) {
    console.error('获取客户列表失败')
  }
}

const showDialog = () => {
  form.value = { order_no: '', agent_id: null, customer_id: null, amount: 0, contract: null, payment: null, delivery: null }
  dialogVisible.value = true
}

const handleFileChange = (file, type) => {
  form.value[type] = file.raw
}

const submitPerformance = async () => {
  try {
    await api.createPerformance({
      order_id: parseInt(form.value.order_no) || 1,
      sales_id: parseInt(localStorage.getItem('userId')) || 1,
      agent_id: form.value.agent_id,
      customer_id: form.value.customer_id,
      product_id: 1, // 默认第一个产品
      quantity: 1,
      lp_price: 1000, // 默认LP价
      pdc_price: 1100, // 默认PDC价
      reward_amount: form.value.amount
    })
    ElMessage.success('提交成功')
    dialogVisible.value = false
    fetchPerformance()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail?.[0]?.msg || '提交失败')
  }
}

const viewDetail = (row) => {
  currentItem.value = row
  detailVisible.value = true
}

const approve = async (row) => {
  try {
    await ElMessageBox.confirm('确认审核通过该业绩？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    })
    await api.approvePerformance(row.id, true)
    ElMessage.success('审核通过')
    fetchPerformance()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

const reject = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入拒绝原因', '拒绝', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputPattern: /\S+/,
      inputErrorMessage: '请输入拒绝原因'
    })
    await api.rejectPerformance(row.id, value)
    ElMessage.success('已拒绝')
    fetchPerformance()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || '操作失败')
    }
  }
}

const getStatusType = (status) => {
  const types = { pending: 'warning', approved: 'success', rejected: 'danger' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }
  return texts[status] || status
}

onMounted(() => {
  fetchPerformance()
  fetchAgents()
  fetchCustomers()
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
.attachment-item {
  margin-top: 10px;
}
</style>
<template>
  <div class="page-container">
    <div class="page-header">
      <h2>代理商管理</h2>
      <el-button type="primary" @click="showDialog">新增代理商</el-button>
    </div>

    <el-table :data="agents" stripe style="width: 100%">
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="contact" label="联系人" />
      <el-table-column prop="phone" label="电话" width="150" />
      <el-table-column prop="level" label="等级" width="100">
        <template #default="{ row }">
          <el-tag :type="getLevelType(row.level)">{{ row.level }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="余额" width="150">
        <template #default="{ row }">
          <span style="color: #f56c6c; font-weight: bold;">
            ¥{{ row.balance?.toFixed(2) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="success" link @click="viewBalance(row)">查看余额</el-button>
          <el-button type="primary" link @click="editAgent(row)">编辑</el-button>
          <el-button type="danger" link @click="deleteAgent(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑代理商' : '新增代理商'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="联系人">
          <el-input v-model="form.contact" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="form.level">
            <el-option label="普通" value="普通" />
            <el-option label="高级" value="高级" />
            <el-option label="VIP" value="VIP" />
          </el-select>
        </el-form-item>
        <el-form-item label="初始余额">
          <el-input-number v-model="form.balance" :precision="2" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveAgent">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="balanceDialogVisible" title="代理商余额详情" width="500px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="代理商">{{ currentAgent?.name }}</el-descriptions-item>
        <el-descriptions-item label="当前余额">
          <span style="color: #f56c6c; font-weight: bold;">
            ¥{{ currentAgent?.balance?.toFixed(2) }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="等级">
          <el-tag :type="getLevelType(currentAgent?.level)">{{ currentAgent?.level }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="联系人">{{ currentAgent?.contact }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="balanceDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const agents = ref([])
const dialogVisible = ref(false)
const balanceDialogVisible = ref(false)
const isEdit = ref(false)
const currentAgent = ref(null)
const form = ref({
  id: null,
  name: '',
  contact: '',
  phone: '',
  level: '普通',
  balance: 0
})

const fetchAgents = async () => {
  try {
    agents.value = await api.getAgents()
  } catch (error) {
    ElMessage.error('获取代理商列表失败')
  }
}

const showDialog = () => {
  isEdit.value = false
  form.value = { id: null, name: '', contact: '', phone: '', level: '普通', balance: 0 }
  dialogVisible.value = true
}

const editAgent = (row) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

const viewBalance = (row) => {
  currentAgent.value = row
  balanceDialogVisible.value = true
}

const saveAgent = async () => {
  try {
    if (isEdit.value) {
      await api.updateAgent(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await api.createAgent(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchAgents()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteAgent = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该代理商吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.deleteAgent(id)
    ElMessage.success('删除成功')
    fetchAgents()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getLevelType = (level) => {
  const types = { 'VIP': 'danger', '高级': 'warning', '普通': 'info' }
  return types[level] || 'info'
}

onMounted(fetchAgents)
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
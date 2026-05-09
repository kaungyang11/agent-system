<template>
  <div class="page-container">
    <div class="page-header">
      <h2>客户管理</h2>
      <el-button type="primary" @click="showDialog">添加客户</el-button>
    </div>

    <el-table :data="customers" stripe style="width: 100%">
      <el-table-column prop="name" label="姓名" />
      <el-table-column prop="phone" label="电话" width="150" />
      <el-table-column prop="agent_name" label="所属代理商" />
      <el-table-column prop="sales_name" label="负责销售" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="editCustomer(row)">编辑</el-button>
          <el-button type="danger" link @click="deleteCustomer(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑客户' : '添加客户'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="姓名">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" />
        </el-form-item>
        <el-form-item label="所属代理商">
          <el-select v-model="form.agent_id" placeholder="选择代理商" filterable clearable>
            <el-option 
              v-for="a in agents" 
              :key="a.id" 
              :label="a.name" 
              :value="a.id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="负责销售">
          <el-input v-model="form.sales_name" placeholder="输入销售姓名" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCustomer">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const customers = ref([])
const agents = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({
  id: null,
  name: '',
  phone: '',
  agent_id: null,
  sales_name: '',
  remark: ''
})

const fetchCustomers = async () => {
  try {
    customers.value = await api.getCustomers()
  } catch (error) {
    ElMessage.error('获取客户列表失败')
  }
}

const fetchAgents = async () => {
  try {
    agents.value = await api.getAgents()
  } catch (error) {
    console.error('获取代理商列表失败')
  }
}

const showDialog = () => {
  isEdit.value = false
  form.value = { id: null, name: '', phone: '', agent_id: null, sales_name: '', remark: '' }
  dialogVisible.value = true
}

const editCustomer = (row) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

const saveCustomer = async () => {
  try {
    if (isEdit.value) {
      await api.updateCustomer(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await api.createCustomer(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchCustomers()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteCustomer = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该客户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.deleteCustomer(id)
    ElMessage.success('删除成功')
    fetchCustomers()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchCustomers()
  fetchAgents()
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
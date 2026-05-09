<template>
  <div class="page-container">
    <div class="page-header">
      <h2>产品管理</h2>
      <el-button type="primary" @click="showDialog">新增产品</el-button>
    </div>

    <el-table :data="products" stripe style="width: 100%">
      <el-table-column prop="name" label="产品名称" />
      <el-table-column prop="code" label="产品编码" width="150" />
      <el-table-column prop="lp_price" label="LP价" width="120">
        <template #default="{ row }">
          ¥{{ row.lp_price?.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="pdc_price" label="PDC价" width="120">
        <template #default="{ row }">
          ¥{{ row.pdc_price?.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="moq" label="MOQ" width="100" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="editProduct(row)">编辑</el-button>
          <el-button type="danger" link @click="deleteProduct(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑产品' : '新增产品'" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="产品名称">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="产品编码">
          <el-input v-model="form.code" />
        </el-form-item>
        <el-form-item label="LP价">
          <el-input-number v-model="form.lp_price" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="PDC价">
          <el-input-number v-model="form.pdc_price" :precision="2" :min="0" />
        </el-form-item>
        <el-form-item label="MOQ">
          <el-input-number v-model="form.moq" :min="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveProduct">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'

const products = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref({
  id: null,
  name: '',
  code: '',
  lp_price: 0,
  pdc_price: 0,
  moq: 1
})

const fetchProducts = async () => {
  try {
    products.value = await api.getProducts()
  } catch (error) {
    ElMessage.error('获取产品列表失败')
  }
}

const showDialog = () => {
  isEdit.value = false
  form.value = { id: null, name: '', code: '', lp_price: 0, pdc_price: 0, moq: 1 }
  dialogVisible.value = true
}

const editProduct = (row) => {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

const saveProduct = async () => {
  try {
    if (isEdit.value) {
      await api.updateProduct(form.value.id, form.value)
      ElMessage.success('更新成功')
    } else {
      await api.createProduct(form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchProducts()
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteProduct = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除该产品吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await api.deleteProduct(id)
    ElMessage.success('删除成功')
    fetchProducts()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(fetchProducts)
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
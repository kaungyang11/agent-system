<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>代理商销售管理系统</h2>
      </template>

      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password @keyup.enter="handleLogin" />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleLogin" style="width: 100%" :loading="loading">
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()
const loading = ref(false)
const form = reactive({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!form.username || !form.password) {
    ElMessage.warning('请填写用户名和密码')
    return
  }

  loading.value = true
  try {
    const response = await api.login({
      username: form.username,
      password: form.password
    })

    // 保存token
    localStorage.setItem('token', response.access_token)
    localStorage.setItem('username', form.username)

    // 获取用户信息
    const profile = await api.getProfile()
    localStorage.setItem('role', profile.role)
    localStorage.setItem('userId', profile.id)

    ElMessage.success('登录成功')

    // 根据角色跳转到不同页面
    const rolePages = {
      'admin': '/',
      'sales': '/',
      'agent': '/',
      'customer': '/'
    }
    router.push(rolePages[profile.role] || '/')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
}

.login-card h2 {
  text-align: center;
  color: #333;
}
</style>
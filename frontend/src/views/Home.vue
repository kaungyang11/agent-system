<template>
  <div class="home-container">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>🏢 代理商销售管理系统</h1>
          <div class="header-right">
            <el-button v-if="!isLoggedIn" type="primary" @click="$router.push('/login')">
              登录系统
            </el-button>
            <span v-else>欢迎，{{ username }} ({{ roleText }})</span>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card shadow="hover" @click="$router.push('/login')">
              <div class="stat-card">
                <h3>👔 销售</h3>
                <p>客户管理、业绩统计</p>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" @click="$router.push('/login')">
              <div class="stat-card">
                <h3>🤝 代理商</h3>
                <p>采购备货、订单处理</p>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" @click="$router.push('/login')">
              <div class="stat-card">
                <h3>🛒 客户</h3>
                <p>浏览产品、下单购买</p>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card shadow="hover" @click="$router.push('/login')">
              <div class="stat-card">
                <h3>🏢 管理员</h3>
                <p>系统管理、业绩记录</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-card style="margin-top: 20px">
          <template #header>
            <h3>📋 系统简介</h3>
          </template>
          <p>代理商销售管理系统是一个用于管理代理商、销售、客户之间业务关系的系统。</p>
          <el-timeline>
            <el-timeline-item timestamp="算能" placement="top">
              <h4>算能（源头）</h4>
              <p>产品管理、定价LP、代理商管理</p>
            </el-timeline-item>
            <el-timeline-item timestamp="代理商" placement="top">
              <h4>代理商</h4>
              <p>采购备货（MOQ）、库存管理、发货给客户</p>
            </el-timeline-item>
            <el-timeline-item timestamp="客户" placement="top">
              <h4>最终客户</h4>
              <p>向代理商购买产品</p>
            </el-timeline-item>
            <el-timeline-item timestamp="销售" placement="top">
              <h4>销售</h4>
              <p>跟进客户、协助下单、业绩统计</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const isLoggedIn = computed(() => !!localStorage.getItem('token'))
const username = computed(() => localStorage.getItem('username') || '用户')
const role = computed(() => localStorage.getItem('role'))

const roleText = computed(() => {
  const map = {
    'admin': '算能管理员',
    'sales': '销售',
    'agent': '代理商',
    'customer': '客户'
  }
  return map[role.value] || role.value
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
}

.el-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  margin: 0;
  font-size: 20px;
}

.header-right {
  color: white;
}

.stat-card {
  text-align: center;
  cursor: pointer;
}

.stat-card h3 {
  margin: 0 0 10px 0;
  color: #667eea;
}

.stat-card p {
  margin: 0;
  color: #666;
  font-size: 12px;
}
</style>
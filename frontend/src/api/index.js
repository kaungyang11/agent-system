import axios from 'axios'

// 根据环境选择 API 地址
const isProd = import.meta.env.PROD
const API_BASE = isProd ? 'http://localhost:8000/api' : '/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理错误
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const api = {
  // 认证
  login: (data) => apiClient.post('/auth/login', data),
  logout: () => apiClient.post('/auth/logout'),
  getProfile: () => apiClient.get('/auth/me'),
  
  // 产品
  getProducts: (params) => apiClient.get('/products', { params }),
  getProduct: (id) => apiClient.get(`/products/${id}`),
  createProduct: (data) => apiClient.post('/products', data),
  updateProduct: (id, data) => apiClient.put(`/products/${id}`, data),
  deleteProduct: (id) => apiClient.delete(`/products/${id}`),
  
  // 订单
  getOrders: (params) => apiClient.get('/orders', { params }),
  getOrder: (id) => apiClient.get(`/orders/${id}`),
  createOrder: (data) => apiClient.post('/orders', data),
  updateOrder: (id, data) => apiClient.put(`/orders/${id}`, data),
  deleteOrder: (id) => apiClient.delete(`/orders/${id}`),
  
  // 客户
  getCustomers: (params) => apiClient.get('/customers', { params }),
  getCustomer: (id) => apiClient.get(`/customers/${id}`),
  createCustomer: (data) => apiClient.post('/customers', data),
  updateCustomer: (id, data) => apiClient.put(`/customers/${id}`, data),
  deleteCustomer: (id) => apiClient.delete(`/customers/${id}`),
  
  // 代理商
  getAgents: (params) => apiClient.get('/agents', { params }),
  getAgent: (id) => apiClient.get(`/agents/${id}`),
  createAgent: (data) => apiClient.post('/agents', data),
  updateAgent: (id, data) => apiClient.put(`/agents/${id}`, data),
  deleteAgent: (id) => apiClient.delete(`/agents/${id}`),
  getAgentBalance: (id) => apiClient.get(`/agents/${id}/balance`),
  
  // 库存
  getInventory: (params) => apiClient.get('/inventory', { params }),
  createInventory: (data) => apiClient.post('/inventory', data),
  updateInventory: (id, data) => apiClient.put(`/inventory/${id}`, data),
  stockIn: (data) => apiClient.post('/inventory/stock-in', data),
  stockOut: (data) => apiClient.post('/inventory/stock-out', data),
  
  // 业绩
  getPerformance: (params) => apiClient.get('/performance', { params }),
  getPerformanceDetail: (id) => apiClient.get(`/performance/${id}`),
  createPerformance: (data) => apiClient.post('/performance', data),
  updatePerformance: (id, data) => apiClient.put(`/performance/${id}`, data),
  approvePerformance: (id, approved = true) => apiClient.put(`/performance/${id}/approve`, { approved }),
  rejectPerformance: (id, remark) => apiClient.put(`/performance/${id}/reject?remark=${encodeURIComponent(remark)}`),
  settlePerformance: (id) => apiClient.post(`/performance/${id}/settle`, { settled: true })
}

export default api
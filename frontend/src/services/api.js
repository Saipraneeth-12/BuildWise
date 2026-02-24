import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const auth = {
  signup: (data) => api.post('/auth/signup', data),
  login: (data) => api.post('/auth/login', data),
  getProfile: () => api.get('/auth/profile')
}

export const chat = {
  sendMessage: (message) => api.post('/chat', { message }),
  getHistory: () => api.get('/chat/history')
}

export const materials = {
  estimate: (data) => api.post('/materials/estimate', data)
}

export const cost = {
  calculate: (data) => api.post('/cost/calculate', data)
}

export const projects = {
  getAll: () => api.get('/projects'),
  create: (data) => api.post('/projects', data),
  update: (id, data) => api.put(`/projects/${id}`, data)
}

export const expenses = {
  getAll: () => api.get('/expenses'),
  create: (data) => api.post('/expenses', data)
}

export const reminders = {
  getAll: () => api.get('/reminders'),
  create: (data) => api.post('/reminders', data)
}

export const documents = {
  getAll: () => api.get('/documents'),
  upload: (data) => api.post('/documents', data),
  delete: (id) => api.delete(`/documents/${id}`)
}

export const tasks = {
  getAll: (projectId) => api.get('/tasks', { params: { project_id: projectId } }),
  create: (data) => api.post('/tasks', data),
  update: (id, data) => api.put(`/tasks/${id}`, data),
  delete: (id) => api.delete(`/tasks/${id}`),
  generateWithAI: (data) => api.post('/tasks/generate', data)
}

export const architecture = {
  generateWithAI: (data) => api.post('/architecture/generate', data),
  getBlueprints: () => api.get('/architecture/blueprints'),
  deleteBlueprint: (id) => api.delete(`/architecture/blueprints/${id}`),
  saveDrawing: (data) => api.post('/architecture/save-drawing', data),
  saveBlueprintToDocuments: (data) => api.post('/architecture/save-blueprint-to-docs', data)
}

export const scrum = {
  generate: (data) => api.post('/scrum/generate', data),
  handleDelay: (data) => api.post('/scrum/delay', data),
  updateChecklist: (data) => api.post('/scrum/checklist', data),
  getSchedules: () => api.get('/scrum/schedules')
}

export const budget = {
  get: () => api.get('/budget'),
  update: (data) => api.put('/budget', data)
}

export const analytics = {
  getDashboard: () => api.get('/analytics/dashboard'),
  getReports: () => api.get('/analytics/reports')
}

export const materialPrices = {
  getLive: (params) => api.get('/materials/live', { params }),
  getHistory: (params) => api.get('/materials/history', { params }),
  getTrends: () => api.get('/materials/trends'),
  getSummary: () => api.get('/materials/summary'),
  getFilters: () => api.get('/materials/filters'),
  refresh: () => api.post('/materials/refresh')
}

export default api

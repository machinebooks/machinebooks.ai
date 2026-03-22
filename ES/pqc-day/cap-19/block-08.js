// Extraído de: LibroPQC/cap-19-dashboard.md
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,    // 30s — los análisis pueden tardar
  headers: { 'Content-Type': 'application/json' },
})

// Interceptor de petición: añadir JWT a todas las llamadas
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor de respuesta: gestionar 401 globalmente
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'  // Redirección forzada
    }
    return Promise.reject(error)
  }
)

export default api

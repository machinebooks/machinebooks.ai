// Extraído de: LibroCISO/cap-18-react-grc.md
import axios, {
  type AxiosInstance,
  type AxiosError,
  type InternalAxiosRequestConfig,
} from 'axios'
import { useAuthStore } from '@/stores/authStore'

const apiClient: AxiosInstance = axios.create({
  baseURL: '',           // Vite proxy reenvía /api/* → FastAPI
  timeout: 30_000,       // 30s — suficiente para operaciones IA pesadas
  headers: {
    'Content-Type': 'application/json',
    'X-Client-Version': import.meta.env.VITE_APP_VERSION ?? '1.0.0',
  },
})

// ── Request interceptor: JWT + idempotencia ──────────────────
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // Inyecta el token JWT en cada petición
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`
  }
  // Clave de idempotencia para mutaciones → evita duplicados por retry
  if (['post', 'put', 'patch'].includes(config.method ?? '')) {
    config.headers['Idempotency-Key'] = crypto.randomUUID()
  }
  return config
})

// ── Response interceptor: refresh token automático ───────────
let refreshPromise: Promise<string> | null = null

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean
    }

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true

      const refreshToken = useAuthStore.getState().refreshToken
      if (!refreshToken) {
        useAuthStore.getState().logout()
        window.location.href = '/login'
        return Promise.reject(error)
      }

      // Reutiliza la misma promesa si hay refresh concurrente
      if (!refreshPromise) {
        refreshPromise = apiClient
          .post('/api/v1/auth/refresh', { refresh_token: refreshToken })
          .then((res) => {
            const { access_token, refresh_token: newRefresh } = res.data
            useAuthStore.getState().setTokens(access_token, newRefresh)
            return access_token
          })
          .catch(() => {
            useAuthStore.getState().logout()
            window.location.href = '/login'
            throw error
          })
          .finally(() => { refreshPromise = null })
      }

      const newToken = await refreshPromise
      original.headers['Authorization'] = `Bearer ${newToken}`
      return apiClient(original)
    }
    return Promise.reject(error)
  }
)

export default apiClient

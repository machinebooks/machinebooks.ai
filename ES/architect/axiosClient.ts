// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// axiosClient.ts — Cliente HTTP centralizado para los tres frontales
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';

// La URL base se inyecta en tiempo de build desde variables de entorno
const BASE_URL = import.meta.env.VITE_API_URL || 'https://api.ejemplo.com';

const axiosClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,    // 30 segundos: suficiente para la mayoría de operaciones
  headers: {
    'Content-Type': 'application/json',
  },
});

// Control de concurrencia para el refresco de token
// Evita que múltiples 401 simultáneos disparen múltiples peticiones de refresco
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: AxiosError) => void;
}> = [];

function processQueue(error: AxiosError | null, token: string | null) {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token!);
    }
  });
  failedQueue = [];
}

// Interceptor de petición: inyecta el JWT en cada llamada saliente
axiosClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // [WARN] localStorage es vulnerable a XSS — mitigado por CSP estricta (ver sección Nginx)
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);


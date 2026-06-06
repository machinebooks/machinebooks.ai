// Extracted from: LibroAIGateway/cap-27-frontend-architecture-realtime.md
// admin-panel/src/services/api.ts — Axios with interceptors
import axios from 'axios';

const api = axios.create({
  baseURL: '',               // same origin: Vite's proxy routes to the API
  timeout: 15_000,
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('n7x_auth_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  const orgId = sessionStorage.getItem('n7x_organization_id');
  if (orgId) config.headers['X-Organization-ID'] = orgId;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401) await handleTokenRefresh(err.config);
    return Promise.reject(err);
  },
);

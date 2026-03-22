// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// Interceptor de respuesta: gestiona la expiración del token y los errores globales
axiosClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // Si recibimos un 401 y no hemos intentado el refresco todavía
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Si ya hay un refresco en curso, encolamos esta petición
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              originalRequest.headers['Authorization'] = `Bearer ${token}`;
              resolve(axiosClient(originalRequest));
            },
            reject,
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');

      if (!refreshToken) {
        // Sin refresh token: logout inmediato
        processQueue(error, null);
        isRefreshing = false;
        window.dispatchEvent(new CustomEvent('auth:logout'));
        return Promise.reject(error);
      }


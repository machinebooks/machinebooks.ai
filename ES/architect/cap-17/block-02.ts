// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
      try {
        // Llamada directa (sin el interceptor) al endpoint de refresco
        const response = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token: newRefreshToken } = response.data;

        localStorage.setItem('access_token', access_token);
        if (newRefreshToken) {
          // El refresh token (7d) tiene mayor riesgo que el access token (1h) en localStorage
          localStorage.setItem('refresh_token', newRefreshToken);
        }

        axiosClient.defaults.headers.common['Authorization'] =
          `Bearer ${access_token}`;

        processQueue(null, access_token);
        return axiosClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError as AxiosError, null);
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.dispatchEvent(new CustomEvent('auth:logout'));
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default axiosClient;

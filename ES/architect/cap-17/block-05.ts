// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
  const login = useCallback(
    async (email: string, password: string, appName: string) => {
      const response = await axiosClient.post('/auth/login', {
        email,
        password,
        app_name: appName,
      });

      const { access_token, refresh_token, user: userProfile } = response.data;

      localStorage.setItem('access_token', access_token);
      // El refresh token (7d) tiene mayor riesgo que el access token (1h) en localStorage
      localStorage.setItem('refresh_token', refresh_token);
      setUser(userProfile);
    },
    []
  );

  const logout = useCallback(() => {
    // Notificamos al backend para invalidar el token en el servidor
    axiosClient.post('/auth/logout').catch(() => {
      // El logout local se ejecuta incluso si el backend no responde
    });
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
    navigate('/login');
    toast.success('Sesión cerrada correctamente.');
  }, [navigate]);


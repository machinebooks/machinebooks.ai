// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
  const execute = useCallback(
    async (...args: A): Promise<T | null> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      try {
        const result = await apiFn(...args);
        setState({ data: result, isLoading: false, error: null });

        if (options.showSuccessToast && options.successMessage) {
          toast.success(options.successMessage);
        }

        return result;
      } catch (err) {
        const axiosError = err as AxiosError<{ message?: string; error?: string }>;

        // Extraemos el mensaje de error del cuerpo de la respuesta si existe
        const serverMessage =
          axiosError.response?.data?.message ||
          axiosError.response?.data?.error;

        // El mensaje final: primero el del servidor, luego el por defecto del hook,
        // luego un genérico
        const errorMessage =
          serverMessage ||
          options.errorMessage ||
          'Ha ocurrido un error. Por favor, inténtalo de nuevo.';

        setState({ data: null, isLoading: false, error: errorMessage });

        // Los errores 401 no se muestran como toast: el interceptor de Axios
        // ya gestiona el logout y muestra su propio mensaje
        if (axiosError.response?.status !== 401) {
          toast.error(errorMessage);
        }

        return null;
      }
    },
    [apiFn, options]
  );

  return { ...state, execute };
}

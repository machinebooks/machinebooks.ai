// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// Ejemplo de manejo diferenciado en useApiCall extendido
const handleError = (error: AxiosError<ApiError>) => {
  const status = error.response?.status;
  const data = error.response?.data;

  if (status === 422 && data?.details) {
    // Errores de validación: los devolvemos para que el formulario los distribuya
    return { type: 'validation', details: data.details };
  }

  if (status === 403) {
    toast('No tienes permisos para realizar esta acción.', {
      icon: '[WARN]',
      style: { background: '#FEF3C7', color: '#92400E' },
    });
    return { type: 'forbidden' };
  }

  if (status && status >= 500) {
    toast.error('El servicio no está disponible. Inténtalo más tarde.');
    return { type: 'server' };
  }

  toast.error(data?.message || 'Ha ocurrido un error inesperado.');
  return { type: 'unknown' };
};

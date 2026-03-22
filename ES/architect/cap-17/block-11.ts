// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// Mutación para actualizar el estado de una operación
export function useUpdateOperationStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      status,
    }: {
      id: number;
      status: string;
    }) =>
      axiosClient
        .patch(`/operations/${id}/status`, { status })
        .then((r) => r.data),

    onSuccess: (updatedOperation: Operation) => {
      // Actualización optimista de la caché: actualizamos el detalle
      // y marcamos la lista como obsoleta para que se recargue
      queryClient.setQueryData(
        operationKeys.detail(updatedOperation.id),
        updatedOperation
      );
      queryClient.invalidateQueries({ queryKey: operationKeys.lists() });
      toast.success('Estado actualizado correctamente.');
    },

    onError: () => {
      toast.error('No se pudo actualizar el estado. Inténtalo de nuevo.');
    },
  });
}

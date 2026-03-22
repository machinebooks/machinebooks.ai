// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// usePaginatedQuery.ts — Hook genérico para listas paginadas con React Query
import { useQuery } from '@tanstack/react-query';
import axiosClient from '../api/axiosClient';
import type { PaginatedResponse } from '../types/api/models';

interface PaginationParams {
  page: number;
  perPage: number;
  filters?: Record<string, string | number | boolean>;
}

export function usePaginatedQuery<T>(
  endpoint: string,
  params: PaginationParams,
  queryKey: string[]
) {
  return useQuery<PaginatedResponse<T>>({
    queryKey: [...queryKey, params],
    queryFn: async () => {
      const response = await axiosClient.get<PaginatedResponse<T>>(endpoint, {
        params: {
          page: params.page,
          per_page: params.perPage,
          ...params.filters,
        },
      });
      return response.data;
    },
    // Mantener los datos anteriores visibles mientras carga la página nueva
    // evita el parpadeo en la tabla durante la paginación
    placeholderData: (previousData) => previousData,
    staleTime: 30_000,  // 30 segundos antes de considerar los datos obsoletos
  });
}

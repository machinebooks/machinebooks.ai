// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// useOperations.ts — Hooks de React Query para el módulo de operaciones
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axiosClient from '../api/axiosClient';
import toast from 'react-hot-toast';
import type { Operation, PaginatedResponse } from '../types/api/models';

// Claves de consulta centralizadas: facilitan la invalidación coordinada
export const operationKeys = {
  all: ['operations'] as const,
  lists: () => [...operationKeys.all, 'list'] as const,
  list: (filters: object) => [...operationKeys.lists(), filters] as const,
  details: () => [...operationKeys.all, 'detail'] as const,
  detail: (id: number) => [...operationKeys.details(), id] as const,
};

// Hook para lista paginada de operaciones
export function useOperationsList(page: number, filters: object = {}) {
  return useQuery<PaginatedResponse<Operation>>({
    queryKey: operationKeys.list({ page, ...filters }),
    queryFn: () =>
      axiosClient
        .get('/operations', { params: { page, ...filters } })
        .then((r) => r.data),
    staleTime: 30_000,
  });
}

// Hook para el detalle de una operación
export function useOperation(id: number) {
  return useQuery<Operation>({
    queryKey: operationKeys.detail(id),
    queryFn: () =>
      axiosClient.get(`/operations/${id}`).then((r) => r.data),
    enabled: !!id,  // No ejecutar si id es 0 o undefined
  });
}


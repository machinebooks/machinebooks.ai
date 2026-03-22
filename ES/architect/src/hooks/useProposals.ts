// Extraído de: LibroTecnico/cap-16-react-ia.md
// src/hooks/useProposals.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/api/client'
import type { Proposal, CreateProposalPayload } from '@shared/types'

// Query key factory: garantiza consistencia en invalidaciones
const proposalKeys = {
  all: ['proposals'] as const,
  list: (filters: Record<string, unknown>) =>
    [...proposalKeys.all, 'list', filters] as const,
  detail: (id: number) => [...proposalKeys.all, 'detail', id] as const,
}

// Hook para listado con filtros y paginación
export function useProposals(filters: Record<string, unknown> = {}) {
  return useQuery({
    queryKey: proposalKeys.list(filters),
    queryFn: () => apiClient.get<Proposal[]>('/proposals', { params: filters }),
    staleTime: 2 * 60 * 1000,    // 2 minutos antes de refetch
    gcTime: 10 * 60 * 1000,      // 10 minutos en caché tras desmontaje
  })
}

// Hook para detalle de una propuesta
export function useProposal(id: number) {
  return useQuery({
    queryKey: proposalKeys.detail(id),
    queryFn: () => apiClient.get<Proposal>(`/proposals/${id}`),
    enabled: !!id,               // No ejecutar si no hay id
  })
}

// Hook para creación con invalidación automática del listado
export function useCreateProposal() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: CreateProposalPayload) =>
      apiClient.post<Proposal>('/proposals', payload),

    onSuccess: () => {
      // Invalidar todas las queries del listado de propuestas
      queryClient.invalidateQueries({ queryKey: proposalKeys.all })
    },
  })
}

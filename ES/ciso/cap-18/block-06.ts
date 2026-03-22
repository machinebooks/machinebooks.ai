// Extraído de: LibroCISO/cap-18-react-grc.md
import { useQuery, keepPreviousData } from '@tanstack/react-query'

/** Hook genérico: cualquier tabla con paginación servidor sigue este patrón */
export function usePaginatedTable<T>(
  key: string,
  fetcher: (filters: PaginatedFilters) => Promise<PaginatedResponse<T>>,
  filters: PaginatedFilters,
) {
  return useQuery({
    queryKey: [key, filters],
    queryFn: () => fetcher(filters),
    // Mantiene los datos anteriores mientras carga la nueva página
    // → evita flash de pantalla vacía al cambiar de página
    placeholderData: keepPreviousData,
    staleTime: 30_000, // 30s antes de considerar los datos obsoletos
  })
}

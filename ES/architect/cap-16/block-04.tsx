// Extraído de: LibroTecnico/cap-16-react-ia.md
// Patrón de tabla con React Query y sorting local
import { useState } from 'react'
import { useProposals } from '@/hooks/useProposals'
import { type Proposal } from '@shared/types'

type SortField = 'created_at' | 'client_name' | 'status' | 'total_value'
type SortDirection = 'asc' | 'desc'

export function ProposalsTable() {
  const [sortField, setSortField] = useState<SortField>('created_at')
  const [sortDir, setSortDir] = useState<SortDirection>('desc')
  const [page, setPage] = useState(1)

  // React Query gestiona la caché y el estado de carga
  const { data, isLoading, error } = useProposals({
    sort_by: sortField,
    sort_dir: sortDir,
    page,
    per_page: 25,
  })

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDir('asc')
    }
  }

  if (isLoading) return <TableSkeleton columns={5} rows={10} />
  if (error) return <ErrorState message="No se pudieron cargar las propuestas" />

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <SortableHeader
              label="Cliente"
              field="client_name"
              current={sortField}
              direction={sortDir}
              onSort={handleSort}
            />
            {/* ... más columnas */}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {data?.items.map(proposal => (
            <ProposalRow key={proposal.id} proposal={proposal} />
          ))}
        </tbody>
      </table>
      <Pagination
        total={data?.total ?? 0}
        page={page}
        perPage={25}
        onPageChange={setPage}
      />
    </div>
  )
}

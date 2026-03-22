// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// Uso combinado en un componente: los filtros de Zustand alimentan la query de React Query
function OperationsListView() {
  const { activeFilters } = useOperationsUIStore();
  const [page, setPage] = useState(1);

  // Cuando activeFilters cambia, React Query recarga automáticamente
  const { data, isLoading } = useOperationsList(page, activeFilters);

  // ...
}

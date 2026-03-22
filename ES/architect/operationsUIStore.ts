// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// operationsUIStore.ts — Estado de la interfaz del módulo de operaciones
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface OperationsUIState {
  // Estado del panel de detalles
  selectedOperationId: number | null;
  isDetailPanelOpen: boolean;

  // Estado de los filtros activos
  activeFilters: {
    status: string[];
    priority: string[];
    assignedTo: number | null;
    dateRange: [string, string] | null;
  };

  // Estado de la selección en tabla
  selectedIds: Set<number>;

  // Acciones
  selectOperation: (id: number) => void;
  closeDetailPanel: () => void;
  setFilter: (key: string, value: unknown) => void;
  clearFilters: () => void;
  toggleSelection: (id: number) => void;
  clearSelection: () => void;
}

export const useOperationsUIStore = create<OperationsUIState>()(
  devtools(
    (set) => ({
      selectedOperationId: null,
      isDetailPanelOpen: false,
      activeFilters: {
        status: [],
        priority: [],
        assignedTo: null,
        dateRange: null,
      },
      selectedIds: new Set(),

      selectOperation: (id) =>
        set({ selectedOperationId: id, isDetailPanelOpen: true }),

      closeDetailPanel: () =>
        set({ selectedOperationId: null, isDetailPanelOpen: false }),

      setFilter: (key, value) =>
        set((state) => ({
          activeFilters: { ...state.activeFilters, [key]: value },
        })),

      clearFilters: () =>
        set({
          activeFilters: {
            status: [],
            priority: [],
            assignedTo: null,
            dateRange: null,
          },
        }),


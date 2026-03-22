// Extraído de: LibroCISO/cap-18-react-grc.md
import { create } from 'zustand'
import { licensingApi, type ModuleDefinition } from '@/api/licensing'

interface ModulesState {
  /** Claves de módulos activos para el tenant actual */
  activeModules: string[]
  /** Catálogo completo de módulos de la Plataforma */
  catalog: ModuleDefinition[]
  /** Indica si ya se cargó al menos una vez (evita flash) */
  loaded: boolean
  error: string | null

  fetch: () => Promise<void>
  hasModule: (key: string) => boolean
  hasAnyModule: (...keys: string[]) => boolean
  reset: () => void
}

export const useModulesStore = create<ModulesState>()((set, get) => ({
  activeModules: [],
  catalog: [],
  loaded: false,
  error: null,

  fetch: async () => {
    try {
      const [activeModules, catalog] = await Promise.all([
        licensingApi.getActiveModules(),
        licensingApi.getCatalog(),
      ])
      set({ activeModules, catalog, loaded: true, error: null })
    } catch (err) {
      // Fallback: módulos core siempre disponibles
      set({
        activeModules: ['dashboard', 'documents', 'reports', 'projects'],
        catalog: [],
        loaded: true,
        error: err instanceof Error ? err.message : 'Error cargando módulos',
      })
    }
  },

  hasModule: (key) => get().activeModules.includes(key),
  hasAnyModule: (...keys) => keys.some((k) => get().activeModules.includes(k)),
  reset: () => set({ activeModules: [], catalog: [], loaded: false, error: null }),
}))

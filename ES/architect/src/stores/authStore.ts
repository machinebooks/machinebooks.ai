// Extraído de: LibroTecnico/cap-16-react-ia.md
// src/stores/authStore.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UserPermissions {
  modules: Record<string, string[]>     // { clients: ['read', 'write'], proposals: ['read'] }
  ai_modules: string[]                  // ['document_analyzer', 'proposal_generator']
  is_admin: boolean
}

interface AuthState {
  token: string | null
  user: {
    id: number
    name: string
    email: string
    app_role: string                    // Rol en la aplicación activa
    app_code: string                    // 'operations' | 'analytics' | 'admin'
  } | null
  permissions: UserPermissions | null
  setAuth: (token: string, user: AuthState['user'], permissions: UserPermissions) => void
  clearAuth: () => void
  hasPermission: (module: string, action: string) => boolean
  hasAiModule: (moduleCode: string) => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      permissions: null,

      setAuth: (token, user, permissions) =>
        set({ token, user, permissions }),

      clearAuth: () =>
        set({ token: null, user: null, permissions: null }),

      // Verificación de permiso: consulta el JSON de permisos del rol
      hasPermission: (module, action) => {
        const perms = get().permissions
        if (!perms) return false
        if (perms.is_admin) return true
        return perms.modules[module]?.includes(action) ?? false
      },

      // Verificación de acceso a módulo IA
      hasAiModule: (moduleCode) => {
        const perms = get().permissions
        if (!perms) return false
        if (perms.is_admin) return true
        return perms.ai_modules.includes(moduleCode)
      },
    }),
    {
      name: 'auth-storage',             // Clave en localStorage
      partialize: (state) => ({         // Solo persistir lo necesario
        token: state.token,
        user: state.user,
        permissions: state.permissions,
      }),
    }
  )
)

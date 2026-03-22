// Extraído de: LibroTecnico/cap-16-react-ia.md
// src/components/layouts/ProtectedLayout.tsx
import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useTokenRefresh } from '@/hooks/useTokenRefresh'

export function ProtectedLayout() {
  const { token, user } = useAuthStore()
  useTokenRefresh()   // Hook que renueva el token automáticamente

  // Sin token: redirigir a login
  if (!token || !user) {
    return <Navigate to="/login" replace />
  }

  // Verificar que el usuario tiene acceso a esta aplicación
  if (user.app_code !== 'operations') {
    return <Navigate to="/unauthorized" replace />
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}

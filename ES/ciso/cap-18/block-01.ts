// Extraído de: LibroCISO/cap-18-react-grc.md
import { lazy, Suspense } from 'react'
import { createBrowserRouter, Navigate } from 'react-router-dom'
import { useModulesStore } from '@/stores/modulesStore'
import LoadingSpinner from '@/components/common/LoadingSpinner'

// --- Guards ---

/** Redirige a /dashboard si el módulo no está licenciado */
function ModuleGuard({ moduleKey, children }: {
  moduleKey: string
  children: React.ReactNode
}) {
  const hasModule = useModulesStore((s) => s.hasModule)
  const loaded = useModulesStore((s) => s.loaded)
  // Spinner mientras carga → evita flash de redirect
  if (!loaded) return <LoadingSpinner fullPage />
  if (!hasModule(moduleKey)) return <Navigate to="/dashboard" replace />
  return <>{children}</>
}

/** Redirige a /dashboard si la IA está desactivada */
function AiGuard({ children }: { children: React.ReactNode }) {
  const aiEnabled = useSystemStore((s) => s.aiEnabled)
  if (!aiEnabled) return <Navigate to="/dashboard" replace />
  return <>{children}</>
}

// --- Lazy imports: cada módulo = un chunk independiente ---
const DashboardPage = lazy(() => import('@/modules/dashboard/DashboardPage'))
const PrivacyPage = lazy(() => import('@/modules/privacy/PrivacyPage'))
const RiskPage = lazy(() => import('@/modules/risk/RiskPage'))
const CompliancePage = lazy(() => import('@/modules/compliance/CompliancePage'))
const NIS2Page = lazy(() => import('@/modules/nis2/NIS2Page'))
const DORAPage = lazy(() => import('@/modules/dora/DORAPage'))
const AIGovernancePage = lazy(() => import('@/modules/ai-governance/AIGovernancePage'))
// ... 25 módulos más con el mismo patrón

/** Envuelve un componente lazy con Suspense */
const withSuspense = (Component: React.LazyExoticComponent<any>) => (
  <Suspense fallback={<LoadingSpinner fullPage />}>
    <Component />
  </Suspense>
)

/** Módulo licenciable: gate de licencia + suspense */
const withModule = (
  moduleKey: string,
  Component: React.LazyExoticComponent<any>
) => (
  <ModuleGuard moduleKey={moduleKey}>
    {withSuspense(Component)}
  </ModuleGuard>
)

export const router = createBrowserRouter([
  {
    element: <AppLayout />,
    children: [
      // Core (siempre disponible)
      { path: '/dashboard', element: withSuspense(DashboardPage) },

      // Módulos licenciables — solo cargan si el tenant tiene licencia
      { path: '/privacy/*', element: withModule('privacy', PrivacyPage) },
      { path: '/risk/*', element: withModule('risk', RiskPage) },
      { path: '/compliance/*', element: withModule('compliance', CompliancePage) },
      { path: '/nis2/*', element: withModule('nis2', NIS2Page) },
      { path: '/dora/*', element: withModule('dora', DORAPage) },
      { path: '/ai-governance/*', element: withModule('ai_governance', AIGovernancePage) },
      // ... resto de módulos licenciables
    ],
  },
  { path: '*', element: withSuspense(NotFoundPage) },
])

// Extraído de: LibroTecnico/cap-16-react-ia.md
// src/router/index.tsx — Router principal de App Principal
import { createBrowserRouter } from 'react-router-dom'
import { ProtectedLayout } from '@/components/layouts/ProtectedLayout'
import { proposalRoutes } from '@/modules/proposals/routes'
import { clientRoutes } from '@/modules/clients/routes'
import { documentRoutes } from '@/modules/documents/routes'
import { opportunityRoutes } from '@/modules/opportunities/routes'
// ... 19 módulos más

export const router = createBrowserRouter([
  {
    path: '/',
    element: <ProtectedLayout />,         // Auth + layout general
    children: [
      ...proposalRoutes,
      ...clientRoutes,
      ...documentRoutes,
      ...opportunityRoutes,
      // ... resto de módulos
    ],
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
])

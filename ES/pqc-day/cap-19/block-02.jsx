// Extraído de: LibroPQC/cap-19-dashboard.md
import { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import Layout from './components/layout/Layout'
import Login from './pages/Auth/Login'
import Register from './pages/Auth/Register'
import Dashboard from './pages/Dashboard/Dashboard'
import ClientsList from './pages/Clients/ClientsList'
import ClientDetail from './pages/Clients/ClientDetail'
import AnalysisList from './pages/Analysis/AnalysisList'
import AnalysisDetail from './pages/Analysis/AnalysisDetail'
import NewAnalysis from './pages/Analysis/NewAnalysis'
import URLAnalysis from './pages/Analysis/URLAnalysis'
import AICodeAnalyzer from './pages/Analysis/AICodeAnalyzer'
import CloudSecurity from './pages/Cloud/CloudSecurity'
import ComplianceList from './pages/Compliance/ComplianceList'
import AuditLogs from './pages/Audit/AuditLogs'
import { AdminIA } from './pages/AdminIA'
import { authApi } from './api'
import { setUser, logout } from './store/slices/authSlice'

function App() {
  const dispatch = useDispatch()
  const { isAuthenticated, user, token } = useSelector((s) => s.auth)

  // Verificar token al cargar la aplicación
  useEffect(() => {
    const loadProfile = async () => {
      if (token && !user) {
        try {
          const res = await authApi.me()
          dispatch(setUser(res.data))
        } catch {
          dispatch(logout())   // Token inválido → cerrar sesión
        }
      }
    }
    loadProfile()
  }, [token, user, dispatch])

  return (
    <Routes>
      {/* Rutas públicas — sin layout */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Rutas protegidas — dentro del layout con sidebar */}
      <Route path="/" element={
        <PrivateRoute><Layout /></PrivateRoute>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="clients" element={<ClientsList />} />
        <Route path="clients/:id" element={<ClientDetail />} />
        <Route path="analysis" element={<AnalysisList />} />
        <Route path="analysis/new" element={<NewAnalysis />} />
        <Route path="analysis/url" element={<URLAnalysis />} />
        <Route path="analysis/ai" element={<AICodeAnalyzer />} />
        <Route path="analysis/:id" element={<AnalysisDetail />} />
        <Route path="cloud" element={<CloudSecurity />} />
        <Route path="compliance" element={<ComplianceList />} />
        <Route path="audit" element={<AuditLogs />} />
        <Route path="admin/ia" element={<AdminIA />} />
      </Route>

      {/* Cualquier ruta desconocida → dashboard */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

function PrivateRoute({ children }) {
  const { isAuthenticated } = useSelector((s) => s.auth)
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

export default App

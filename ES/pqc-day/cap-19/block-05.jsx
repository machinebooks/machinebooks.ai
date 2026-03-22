// Extraído de: LibroPQC/cap-19-dashboard.md
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Typography, Box, Grid, Card, CardContent,
  CircularProgress, Paper, Chip, Alert,
  LinearProgress, Table, TableBody, TableCell,
  TableHead, TableRow,
} from '@mui/material'
import { dashboardApi } from '../../api'

export default function Dashboard() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [stats, setStats] = useState({
    total_clients: 0,
    total_findings: 0,
    critical_findings: 0,
    pqc_readiness_avg: 0,
    findings_by_severity: { critical: 0, high: 0, medium: 0, low: 0 },
    findings_by_category: {
      pqc: { total: 0, critical: 0, high: 0, medium: 0, low: 0 },
      owasp: { total: 0, critical: 0, high: 0, medium: 0, low: 0 },
      cloud: { total: 0, critical: 0, high: 0, medium: 0, low: 0 },
    },
    recent_analysis: [],
    clients_by_status: { active: 0, inactive: 0 },
  })

  useEffect(() => {
    loadDashboard()
    // Actualización automática cada 30 segundos
    const interval = setInterval(loadDashboard, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadDashboard = async () => {
    try {
      const response = await dashboardApi.getStats()
      setStats(response.data)
    } catch (err) {
      setError('Error al cargar estadísticas')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" minHeight="400px">
        <CircularProgress />
      </Box>
    )
  }

  return (
    <Box>
      {/* Cabecera con título y controles */}
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Dashboard PQC
      </Typography>

      {/* Fila 1: Tarjetas de KPI principales */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} lg={3}>
          <KPICard
            label="Clientes"
            value={stats.total_clients}
            subtitle={`${stats.clients_by_status?.active || 0} activos`}
            gradient="linear-gradient(135deg, #667eea, #764ba2)"
            onClick={() => navigate('/clients')}
          />
        </Grid>
        <Grid item xs={12} sm={6} lg={3}>
          <KPICard
            label="Hallazgos"
            value={stats.total_findings}
            subtitle={`${stats.critical_findings} críticos`}
            gradient="linear-gradient(135deg, #f093fb, #f5576c)"
            onClick={() => navigate('/analysis')}
          />
        </Grid>
        {/* ... análisis totales, usuarios */}
      </Grid>

      {/* Fila 2: Hallazgos por categoría (PQC, OWASP, Cloud) */}
      {/* Fila 3: Análisis recientes + Score PQC general */}
    </Box>
  )
}

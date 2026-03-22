// Extraído de: LibroPQC/cap-19-dashboard.md
import { Outlet } from 'react-router-dom'
import {
  Box, AppBar, Toolbar, Typography,
  IconButton, Avatar, Chip, Tooltip,
} from '@mui/material'
import { SecurityOutlined, NotificationsOutlined } from '@mui/icons-material'
import { useSelector } from 'react-redux'
import Sidebar from './Sidebar'

export default function Layout() {
  const { user, organization } = useSelector((s) => s.auth)

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Barra superior — fija, siempre visible */}
      <AppBar
        position="fixed"
        sx={{
          zIndex: (theme) => theme.zIndex.drawer + 1,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        }}
      >
        <Toolbar>
          <SecurityOutlined sx={{ mr: 2, fontSize: 28 }} />
          <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 600 }}>
            PQC Security
          </Typography>
          <Chip
            label={organization?.name || 'Organización'}
            size="small"
            sx={{ mr: 2, bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
          />
          {/* Menú de usuario con avatar, rol y logout */}
        </Toolbar>
      </AppBar>

      {/* Sidebar — permanente, 260px de ancho */}
      <Sidebar />

      {/* Área de contenido — crece para ocupar el espacio restante */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,                      // Espacio para el AppBar fijo
          minHeight: '100vh',
          backgroundColor: '#f8f9fa', // Fondo ligeramente diferente al paper
        }}
      >
        <Outlet />  {/* Aquí se renderiza la página activa */}
      </Box>
    </Box>
  )
}

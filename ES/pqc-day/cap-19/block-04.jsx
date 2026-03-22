// Extraído de: LibroPQC/cap-19-dashboard.md
import {
  Drawer, List, ListItem, ListItemButton,
  ListItemIcon, ListItemText, Typography, Box, Divider,
} from '@mui/material'
import {
  Dashboard, Business, Assessment, Security,
  CloudQueue, Psychology, AdminPanelSettings,
} from '@mui/icons-material'
import { useNavigate, useLocation } from 'react-router-dom'

const drawerWidth = 260

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()

  // Resaltado visual de la sección activa
  const isActive = (path) => location.pathname.startsWith(path)

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          bgcolor: '#fafbfc',
          borderRight: '1px solid rgba(0,0,0,0.08)',
        },
      }}
    >
      <List sx={{ px: 1.5, pt: 2 }}>
        {/* Grupo: PRINCIPAL */}
        <SectionLabel text="PRINCIPAL" />
        <NavItem
          icon={<Dashboard />}
          label="Dashboard"
          path="/dashboard"
          active={isActive('/dashboard')}
          onClick={() => navigate('/dashboard')}
        />
        <NavItem
          icon={<Business />}
          label="Clientes"
          path="/clients"
          active={isActive('/clients')}
          onClick={() => navigate('/clients')}
        />

        <Divider sx={{ my: 2 }} />

        {/* Grupo: ANÁLISIS PQC */}
        <SectionLabel text="ANÁLISIS PQC" />
        <NavItem
          icon={<Assessment />}
          label="Panel General"
          subtitle="Todos los análisis"
          active={location.pathname === '/analysis'}
          onClick={() => navigate('/analysis')}
        />
        {/* Análisis de código, infraestructura, cloud... */}

        <Divider sx={{ my: 2 }} />

        {/* Grupo: ADMINISTRACIÓN */}
        <SectionLabel text="ADMINISTRACIÓN" />
        <NavItem
          icon={<AdminPanelSettings />}
          label="Admin Central IA"
          subtitle="Proveedores, prompts, ROI..."
          active={isActive('/admin/ia')}
          onClick={() => navigate('/admin/ia')}
        />
      </List>
    </Drawer>
  )
}

// Extraído de: LibroPQC/cap-19-dashboard.md
import { createTheme } from '@mui/material/styles'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',       // Azul institucional — confianza, seguridad
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#fff',
    },
    secondary: {
      main: '#dc004e',       // Rojo para acciones secundarias y alertas
    },
    error: { main: '#d32f2f' },
    warning: { main: '#ed6c02' },
    success: { main: '#2e7d32' },
    background: {
      default: '#f5f5f5',    // Fondo gris claro — reduce fatiga visual
      paper: '#ffffff',       // Tarjetas y paneles sobre fondo blanco
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontSize: '1.5rem', fontWeight: 500 },
    // Todas las variantes tipográficas con pesos definidos
  },
  shape: {
    borderRadius: 8,          // Bordes redondeados consistentes
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',   // Sin mayúsculas forzadas
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)', // Sombra sutil
        },
      },
    },
  },
})

export default theme

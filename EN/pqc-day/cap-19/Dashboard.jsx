/**
 * PQC-Day and the Machine — Chapter 19
 * Pattern: React Dashboard component with MUI and Redux
 *
 * This is a didactic example from the book, not production code.
 * See chapter 19 for full context and explanation.
 *
 * Requirements: React 18+, Material UI 5+, React Router 6+, Redux Toolkit
 */

import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { Outlet } from 'react-router-dom'
import {
  Box, AppBar, Toolbar, Typography,
  IconButton, Avatar, Chip, Tooltip,
  createTheme, ThemeProvider, CssBaseline,
} from '@mui/material'
import { SecurityOutlined, NotificationsOutlined } from '@mui/icons-material'

// --- Theme ---
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',       // Institutional blue — trust, security
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#fff',
    },
    secondary: {
      main: '#dc004e',       // Red for secondary actions and alerts
    },
    error: { main: '#d32f2f' },
    warning: { main: '#ed6c02' },
    success: { main: '#2e7d32' },
    background: {
      default: '#f5f5f5',    // Light gray background — reduces eye fatigue
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontSize: '1.5rem', fontWeight: 500 },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',   // No forced uppercase
          fontWeight: 500,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
})


// --- Layout ---
function Layout() {
  const user = { name: 'Analyst', role: 'admin' }
  const organization = { name: 'Organization' }

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Top bar — fixed, always visible */}
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
            label={organization?.name || 'Organization'}
            size="small"
            sx={{ mr: 2, bgcolor: 'rgba(255,255,255,0.2)', color: 'white' }}
          />
          <Tooltip title="Notifications">
            <IconButton color="inherit">
              <NotificationsOutlined />
            </IconButton>
          </Tooltip>
          <Tooltip title={user?.name}>
            <Avatar sx={{ ml: 1, width: 32, height: 32 }}>
              {user?.name?.charAt(0) || 'U'}
            </Avatar>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Content area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          mt: 8,
          minHeight: '100vh',
          backgroundColor: '#f8f9fa',
        }}
      >
        <Outlet />
      </Box>
    </Box>
  )
}


// --- App Router ---
function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Routes>
        {/* Public routes — no layout */}
        <Route path="/login" element={<div>Login Page</div>} />

        {/* Protected routes — inside layout with sidebar */}
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="analysis" element={<div>Analysis List</div>} />
          <Route path="analysis/new" element={<div>New Analysis</div>} />
          <Route path="analysis/url" element={<div>URL Analysis</div>} />
          <Route path="analysis/ai" element={<div>AI Code Analyzer</div>} />
          <Route path="cloud" element={<div>Cloud Security</div>} />
          <Route path="compliance" element={<div>Compliance</div>} />
          <Route path="audit" element={<div>Audit Logs</div>} />
          <Route path="admin/ia" element={<div>AI Admin</div>} />
        </Route>

        {/* Unknown routes -> dashboard */}
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </ThemeProvider>
  )
}


// --- Dashboard Page (placeholder) ---
function DashboardPage() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        PQC Readiness Dashboard
      </Typography>
      <Typography color="text.secondary">
        Post-quantum cryptographic posture overview.
        See chapter 19 for the full dashboard implementation.
      </Typography>
    </Box>
  )
}


export default App

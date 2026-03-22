// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// MachineProvider — Con auto-refresh configurable
<MachineProvider autoRefreshInterval={30000}>
  {/* Toda la aplicación tiene acceso al estado de las máquinas */}
  <Router>
    <AppRoutes />
  </Router>
</MachineProvider>

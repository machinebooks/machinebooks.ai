// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// AdminLayout — Panel de administración completo
const AdminLayout: React.FC = () => {
  return (
    <div style={{ position: 'fixed', inset: 0, display: 'flex', flexDirection: 'column' }}>
      <AdminHeader />
      <div style={{ display: 'flex', flex: 1, minHeight: 0 }}>
        <AdminSidebar />
        <main style={{ flex: 1, overflow: 'auto', padding: '1.5rem' }}>
          <Routes>
            <Route path="/" element={<AdminDashboard />} />
            <Route path="/users" element={<UserManagement />} />
            <Route path="/teams" element={<AdminTeams />} />
            <Route path="/workzones" element={<WorkzoneAdmin />} />
            <Route path="/challenges" element={<ChallengeManagement />} />
            <Route path="/actions" element={<AttackManagement />} />
            <Route path="/scenarios" element={<ScenarioManagementAdmin />} />
            <Route path="/playbooks" element={<PlaybookManagement />} />
            <Route path="/machines" element={<MachineManagement />} />
            <Route path="/networks" element={<NetworkManagement />} />
            <Route path="/topology" element={<TopologyBuilder />} />
            <Route path="/audit" element={<AuditPanel />} />
            <Route path="/reports" element={<ReportsSystem />} />
            <Route path="/database" element={<DatabaseManagement />} />
            {/* ... más rutas administrativas */}
          </Routes>
        </main>
      </div>
    </div>
  );
};

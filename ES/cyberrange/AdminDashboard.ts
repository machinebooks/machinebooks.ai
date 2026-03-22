// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// AdminDashboard.tsx — Carga paralela de datos del dashboard
const loadDashboardData = async () => {
  setLoading(true);

  const [statsResponse, activityResponse, healthResponse] =
    await Promise.all([
      adminApi.getDashboardStats(),
      adminApi.getRecentActivity().catch(() => []),
      adminApi.getSystemHealth().catch(() => defaultHealth)
    ]);

  // Mapear snake_case del backend a camelCase del frontend
  setStats({
    totalUsers: statsResponse.total_users,
    activeUsers: statsResponse.active_users,
    totalWorkzones: statsResponse.total_workzones,
    activeScenarios: statsResponse.active_scenarios,
    systemHealth: healthResponse.database.status === 'connected'
      ? 'good' : 'warning',
    uptime: healthResponse.uptime
  });
};

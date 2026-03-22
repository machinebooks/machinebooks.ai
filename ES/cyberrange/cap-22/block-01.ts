// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// AppRoutes — Enrutamiento por rol
const AppRoutes: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Routes>
      <Route path="/login"
        element={isAuthenticated ? <Navigate to="/" /> : <LoginScreen />}
      />
      <Route path="/admin/*" element={
        <ProtectedAdminRoute>
          <AdminLayout />       {/* Sidebar + Header propio + 16 rutas */}
        </ProtectedAdminRoute>
      } />
      <Route path="/user/gaming/*" element={
        <ProtectedRoute>
          <GamingLayout />      {/* Header + 7 rutas de competición */}
        </ProtectedRoute>
      } />
      <Route path="/*" element={
        <ProtectedRoute>
          <MainLayout />        {/* Header + Canvas principal */}
        </ProtectedRoute>
      } />
    </Routes>
  );
};

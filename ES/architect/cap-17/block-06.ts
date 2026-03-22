// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
  // Comprobación de permisos granular: consulta el modelo de permisos JSON del backend
  const hasPermission = useCallback(
    (module: string, action: string): boolean => {
      if (!user) return false;
      const modulePermissions = user.permissions[module];
      return modulePermissions?.includes(action) ?? false;
    },
    [user]
  );

  // Acceso a módulos IA: verifica si el rol del usuario puede usar un módulo concreto
  const hasAIAccess = useCallback(
    (module: string): boolean => {
      if (!user) return false;
      return user.ai_modules_access.includes(module);
    },
    [user]
  );

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        logout,
        hasPermission,
        hasAIAccess,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider');
  }
  return context;
}

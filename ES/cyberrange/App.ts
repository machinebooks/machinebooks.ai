// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// App.tsx — Estructura raíz de la aplicación
const App: React.FC = () => {
  return (
    <TranslationProvider>
      <AuthProvider>
        <ToastProvider>
          <FooterProvider>
            <MachineProvider autoRefreshInterval={30000}>
              <Router>
                <AppRoutes />
              </Router>
            </MachineProvider>
          </FooterProvider>
        </ToastProvider>
      </AuthProvider>
    </TranslationProvider>
  );
};

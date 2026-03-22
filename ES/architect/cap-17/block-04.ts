// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Verificación silenciosa del token al cargar la aplicación
  // Si hay un token válido en localStorage, obtenemos el perfil del usuario
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      axiosClient
        .get('/auth/me')
        .then((res) => setUser(res.data))
        .catch(() => {
          // El token no es válido: limpiamos y dejamos al usuario en login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  // Escuchamos el evento global que dispara el cliente Axios cuando
  // el refresco de token falla definitivamente
  useEffect(() => {
    const handleForcedLogout = () => {
      setUser(null);
      toast.error('Tu sesión ha expirado. Por favor, inicia sesión de nuevo.');
      navigate('/login');
    };

    window.addEventListener('auth:logout', handleForcedLogout);
    return () => window.removeEventListener('auth:logout', handleForcedLogout);
  }, [navigate]);


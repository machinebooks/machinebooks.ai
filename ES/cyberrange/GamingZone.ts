// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// GamingZone.tsx — Catálogo de challenges con mapeo MITRE
const GamingZone: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [selectedCategory, setSelectedCategory] =
    useState<string>('all');
  const [userProgress, setUserProgress] = useState<UserProgress[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const [realChallenges, progressData] = await Promise.all([
        gamingApi.getChallenges(),
        gamingApi.getUserProgress()
      ]);
      setChallenges(realChallenges);
      setUserProgress(progressData);
    };
    fetchData();
  }, []);

  // Cada tipo de challenge tiene su icono y estilo visual
  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'ctf':     return FiFlag;    // Capture The Flag
      case 'crisis':  return FiShield;  // Respuesta a incidentes
      case 'guided':  return FiTarget;  // Ejercicio guiado
      case 'escape':  return FiZap;     // Escape room técnico
      default:        return FiPlay;
    }
  };
};

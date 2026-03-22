// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// Scoreboard.tsx — Tabla de clasificación dual
const Scoreboard: React.FC = () => {
  const { t } = useTranslation();
  const [viewMode, setViewMode] =
    useState<'individual' | 'team'>('individual');
  const [playerScores, setPlayerScores] = useState<PlayerScore[]>([]);
  const [teamScores, setTeamScores] = useState<TeamScore[]>([]);

  const fetchScoreboards = async () => {
    const [leaderboard, stats, teamLeaderboard] =
      await Promise.all([
        gamingApi.getLeaderboard(),
        gamingApi.getScoreboardStats(),
        gamingApi.getTeamLeaderboard()
      ]);
    setPlayerScores(leaderboard);
    setTeamScores(teamLeaderboard);
  };

  // Medallas para los tres primeros puestos
  const RankCell = ({ rank }: { rank: number }) => {
    if (rank === 1)
      return <span className="rank-badge rank-badge-gold">1</span>;
    if (rank === 2)
      return <span className="rank-badge rank-badge-silver">2</span>;
    if (rank === 3)
      return <span className="rank-badge rank-badge-bronze">3</span>;
    return <span style={{
      fontFamily: 'monospace', fontWeight: 700
    }}>{rank}</span>;
  };
};

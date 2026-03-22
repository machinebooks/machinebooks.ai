// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// RealTimeExecutionViewer.tsx — Visor de ejecuciones en vivo
interface LogLine {
  timestamp: string;
  line: string;
  source: 'ansible' | 'powershell' | 'system';
  type: 'output' | 'error' | 'status';
}

const RealTimeExecutionViewer: React.FC<Props> = ({
  sessionId, executionType, onClose
}) => {
  const [logs, setLogs] = useState<LogLine[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);
  const websocketRef = useRef<WebSocket | null>(null);
  const logsEndRef = useRef<HTMLDivElement | null>(null);

  // Persistir logs en localStorage para sobrevivir a recargas
  const persistLogs = (sessionId: string, logs: LogLine[]) => {
    const sessionData = {
      logs,
      timestamp: Date.now(),
      sessionId,
      executionType
    };
    localStorage.setItem(
      `execution_logs_${sessionId}`,
      JSON.stringify(sessionData)
    );
  };

  // Recuperar logs persistidos (máximo 2 horas de antigüedad)
  const loadPersistedLogs = (sessionId: string): LogLine[] => {
    const persisted = localStorage.getItem(
      `execution_logs_${sessionId}`
    );
    if (persisted) {
      const { logs, timestamp } = JSON.parse(persisted);
      if (logs?.length > 0 && Date.now() - timestamp < 7200000) {
        return logs;
      }
    }
    return [];
  };
};

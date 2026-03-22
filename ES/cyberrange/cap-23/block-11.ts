// Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
// Ejemplo didáctico: components/RealTimeExecutionViewer.tsx
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
  const [isPaused, setIsPaused] = useState(false);
  const [seenMessages] = useState<Set<string>>(new Set());
  const websocketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    // Recuperar logs persistidos si es reconexión
    const persisted = loadPersistedLogs(sessionId);
    if (persisted.length > 0) {
      setLogs(persisted);
    }

    // Conectar WebSocket nativo
    const wsUrl = `${config.wsBaseUrl}/ws/${executionType}/${sessionId}`;
    const ws = new WebSocket(wsUrl);
    websocketRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      // Ping inicial para confirmar bidireccionalidad
      ws.send(JSON.stringify({
        type: "ping",
        timestamp: new Date().toISOString()
      }));
    };

    ws.onmessage = (event) => {
      if (isPaused) return;

      const data = JSON.parse(event.data);
      switch (data.type) {
        case 'playbook_output':
        case 'powershell_output':
          addLogLine({
            timestamp: data.timestamp,
            line: data.line,
            source: data.source || 'ansible',
            type: 'output'
          });
          break;

        case 'execution_status':
          // Actualizar estado visual (running, completed, failed)
          setStatus(data);
          break;

        case 'error':
          addLogLine({
            timestamp: data.timestamp,
            line: `ERROR: ${data.message}`,
            source: 'system',
            type: 'error'
          });
          break;
      }
    };

    ws.onclose = () => setIsConnected(false);

    return () => ws.close();
  }, [sessionId, executionType]);

  // Persistir logs en localStorage para supervivencia
  // ante recargas de página
  useEffect(() => {
    if (logs.length > 0) {
      persistLogs(sessionId, logs);
    }
  }, [logs, sessionId]);

  // ... renderizado del visor de logs
};

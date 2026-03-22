// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// WebSocketTerminal.tsx — Terminal embebido con Xterm.js
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import 'xterm/css/xterm.css';

interface ConsoleViewerProps {
  wsUrl: string;
  vmid: number;
  consoleType?: 'terminal' | 'novnc';
  vncCredentials?: {
    vnc_user?: string;
    vnc_password?: string;
  };
  authHeaders?: {
    Cookie?: string;
    CSRFPreventionToken?: string;
  };
  onError?: (error: string) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
}

const ConsoleViewer: React.FC<ConsoleViewerProps> = ({
  wsUrl, vmid, consoleType = 'novnc',
  vncCredentials, authHeaders,
  onError, onConnect, onDisconnect
}) => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const terminalInstance = useRef<Terminal | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const fitAddon = useRef<FitAddon | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<
    'connecting' | 'connected' | 'disconnected' | 'error'
  >('connecting');

  // El FitAddon ajusta automáticamente el terminal al contenedor
  useEffect(() => {
    const handleResize = () => fitAddon.current?.fit();
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      wsRef.current?.close();
      terminalInstance.current?.dispose();
    };
  }, [wsUrl, vmid, consoleType]);

  const connectWebSocket = (terminal: Terminal) => {
    setConnectionStatus('connecting');
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionStatus('connected');
      // Si es noVNC, enviar credenciales VNC inmediatamente
      if (consoleType === 'novnc' && vncCredentials?.vnc_password) {
        ws.send(JSON.stringify({
          username: vncCredentials.vnc_user,
          password: vncCredentials.vnc_password
        }));
      }
      terminal.writeln(
        `\r\nConectado al terminal remoto (VM ${vmid})...\r\n`
      );
      onConnect?.();
    };

    ws.onmessage = (event) => {
      // Los datos del terminal llegan como texto o binario
      terminal.write(typeof event.data === 'string'
        ? event.data
        : new Uint8Array(event.data));
    };
  };
};

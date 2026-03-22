// Extraído de: LibroCyberrange/cap-23-tiempo-real-websocket.md
// Ejemplo didáctico: components/WebSocketTerminal.tsx
const ConsoleViewer: React.FC<ConsoleViewerProps> = ({
  wsUrl, vmid, consoleType, vncCredentials
}) => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] =
    useState<'connecting' | 'connected' | 'disconnected'>('connecting');

  useEffect(() => {
    if (consoleType === 'novnc' || !terminalRef.current) return;

    // Inicializar terminal Xterm.js
    const terminal = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      theme: { background: '#1a1a2e', foreground: '#e0e0e0' }
    });
    const fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);
    terminal.loadAddon(new WebLinksAddon());
    terminal.open(terminalRef.current);
    fitAddon.fit();

    // Conectar WebSocket al proxy de Proxmox
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionStatus('connected');
      // Enviar credenciales VNC si aplica
      if (vncCredentials?.vnc_user) {
        ws.send(JSON.stringify({
          username: vncCredentials.vnc_user,
          password: vncCredentials.vnc_password
        }));
      }
    };

    ws.onmessage = (event) => {
      // Renderizar datos en la terminal
      if (event.data instanceof ArrayBuffer) {
        terminal.write(new TextDecoder().decode(event.data));
      } else if (typeof event.data === 'string') {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'data') terminal.write(data.content);
          else if (data.error) {
            terminal.writeln(`\r\nError: ${data.error}\r\n`);
          }
        } catch {
          terminal.write(event.data); // Texto plano
        }
      }
    };

    // Enviar cada tecla del usuario al servidor
    terminal.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(data);
      }
    });

    ws.onclose = () => setConnectionStatus('disconnected');

    return () => { ws.close(); terminal.dispose(); };
  }, [wsUrl, vmid, consoleType]);

  // ... renderizado con indicador de estado
};

// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// useClaudeStreamFetch.ts — Alternativa con fetch + ReadableStream
// Permite enviar cabeceras Authorization directamente sin stream_id intermedio
export function useClaudeStreamFetch(
  options: UseClaudeStreamOptions = {}
): UseClaudeStreamReturn {
  const [streamText, setStreamText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const fullTextRef = useRef('');

  const stopStream = useCallback(() => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
    setIsStreaming(false);
  }, []);

  const startStream = useCallback(
    async (endpoint: string, payload: object) => {
      setStreamText('');
      fullTextRef.current = '';
      setIsStreaming(true);

      const controller = new AbortController();
      abortControllerRef.current = controller;

      const token = localStorage.getItem('access_token');
      const baseUrl = import.meta.env.VITE_API_URL || 'https://api.ejemplo.com';

      try {
        const response = await fetch(`${baseUrl}${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            // El JWT va en la cabecera estándar, sin necesitar URL params
            Authorization: `Bearer ${token}`,
            Accept: 'text/event-stream',
          },
          body: JSON.stringify(payload),
          signal: controller.signal,
        });

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        if (!response.body) throw new Error('No hay body en la respuesta');


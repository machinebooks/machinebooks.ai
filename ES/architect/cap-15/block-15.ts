// Extraído de: LibroTecnico/cap-15-interfaces-chat.md
// Ejemplo didáctico: patrones/chat/streaming_recovery.tsx

const useStreamingWithRecovery = (sessionId: string) => {
  const [tokens, setTokens] = useState<string>('');
  const lastEventId = useRef<string>('');
  const retryCount = useRef(0);
  const MAX_RETRIES = 3;

  const connect = useCallback(() => {
    const url = lastEventId.current
      ? `/api/chat/stream/${sessionId}?last_event_id=${lastEventId.current}`
      : `/api/chat/stream/${sessionId}`;

    const source = new EventSource(url);

    source.onmessage = (event) => {
      lastEventId.current = event.lastEventId;
      retryCount.current = 0; // Reset en cada mensaje exitoso
      setTokens(prev => prev + JSON.parse(event.data).token);
    };

    source.onerror = () => {
      source.close();
      if (retryCount.current < MAX_RETRIES) {
        retryCount.current++;
        // Backoff exponencial: 1s, 2s, 4s
        setTimeout(connect, 1000 * Math.pow(2, retryCount.current - 1));
      } else {
        setError('La conexión se ha interrumpido. Pulsa para reintentar.');
      }
    };

    return source;
  }, [sessionId]);

  // ...
};

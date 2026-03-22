// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// useClaudeStream.ts — Hook para consumir streams SSE de Claude
import { useState, useCallback, useRef } from 'react';

interface UseClaudeStreamOptions {
  onChunk?: (chunk: string) => void;  // Callback por cada fragmento recibido
  onComplete?: (fullText: string) => void;
  onError?: (error: string) => void;
}

interface UseClaudeStreamReturn {
  streamText: string;
  isStreaming: boolean;
  startStream: (endpoint: string, payload: object) => void;
  stopStream: () => void;
}

export function useClaudeStream(
  options: UseClaudeStreamOptions = {}
): UseClaudeStreamReturn {
  const [streamText, setStreamText] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  // Ref para la conexión EventSource: no dispara renders al cambiar
  const eventSourceRef = useRef<EventSource | null>(null);
  const fullTextRef = useRef('');

  const stopStream = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setIsStreaming(false);
  }, []);

  const startStream = useCallback(
    (endpoint: string, payload: object) => {
      // Limpiamos el texto anterior antes de empezar
      setStreamText('');
      fullTextRef.current = '';
      setIsStreaming(true);

      // SSE nativo no soporta POST directamente, por lo que usamos
      // una petición POST previa para obtener un stream_id efímero,
      // y luego abrimos el EventSource con GET usando ese ID
      const token = localStorage.getItem('access_token');
      const baseUrl = import.meta.env.VITE_API_URL || 'https://api.ejemplo.com';


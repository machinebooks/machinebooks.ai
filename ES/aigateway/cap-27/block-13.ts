// Extraído de: LibroAIGateway/cap-27-frontend-arquitectura-realtime.md
// admin-panel/src/hooks/useRealtimeEvents.ts (forma esencial)
import { useEffect } from 'react';

export function useRealtimeEvents() {
  useEffect(() => {
    const ws = connectWebSocket((event) => {
      // Única responsabilidad: reemitir el evento al bus de window
      window.dispatchEvent(new CustomEvent('n7x:realtime', { detail: event }));
    });
    return () => ws.close();
  }, []);
}

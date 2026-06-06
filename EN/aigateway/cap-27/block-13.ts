// Extracted from: LibroAIGateway/cap-27-frontend-architecture-realtime.md
// admin-panel/src/hooks/useRealtimeEvents.ts (essential form)
import { useEffect } from 'react';

export function useRealtimeEvents() {
  useEffect(() => {
    const ws = connectWebSocket((event) => {
      // Sole responsibility: re-emit the event to the window bus
      window.dispatchEvent(new CustomEvent('n7x:realtime', { detail: event }));
    });
    return () => ws.close();
  }, []);
}

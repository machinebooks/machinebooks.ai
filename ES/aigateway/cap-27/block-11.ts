// Extraído de: LibroAIGateway/cap-27-frontend-arquitectura-realtime.md
// Cálculo del delay de reconexión (dentro del hook de realtime)
const BASE_MS = 1_000;
const MAX_MS = 30_000;
const delay = Math.min(BASE_MS * 2 ** attempt, MAX_MS);
// attempt 0 → 1s, 1 → 2s, 2 → 4s, 3 → 8s, 4 → 16s, 5+ → 30s (tope)

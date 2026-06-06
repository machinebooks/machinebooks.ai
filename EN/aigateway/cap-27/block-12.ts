// Extracted from: LibroAIGateway/cap-27-frontend-architecture-realtime.md
const token = sessionStorage.getItem('n7x_auth_token');
const ws = new WebSocket(
  '/api/v1/realtime/events',          // same origin, via proxy
  [`n7x.auth.bearer.${token}`],
);

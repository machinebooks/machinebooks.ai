// Extraído de: LibroAIGateway/cap-27-frontend-arquitectura-realtime.md
const token = sessionStorage.getItem('n7x_auth_token');
const ws = new WebSocket(
  '/api/v1/realtime/events',          // mismo origen, vía proxy
  [`n7x.auth.bearer.${token}`],
);

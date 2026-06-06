// Extraído de: LibroAIGateway/cap-26-gatewayclient-n7x-mcp.md
export interface N7xConfig {
  gatewayUrl: string;
  bearer: string;
}

export function loadConfig(): N7xConfig {
  const gatewayUrl = (process.env.N7X_GATEWAY_URL || '').replace(/\/+$/, '');
  const bearer = process.env.N7X_BEARER || '';
  if (!gatewayUrl) throw new Error('N7X_GATEWAY_URL no definido');
  if (!bearer) throw new Error('N7X_BEARER no definido');
  return { gatewayUrl, bearer };
}

// Extraído de: LibroAIGateway/cap-26-gatewayclient-n7x-mcp.md
export class GatewayClient {
  constructor(private readonly cfg: N7xConfig) {}

  private buildHeaders(extra?: Record<string, string>): Record<string, string> {
    const headers: Record<string, string> = {
      Authorization: `Bearer ${this.cfg.bearer}`,
      'Content-Type': 'application/json',
    };
    return { ...headers, ...(extra ?? {}) };
  }
}

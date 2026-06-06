// Extracted from: LibroAIGateway/cap-26-gatewayclient-n7x-mcp.md
async get<T>(path: string): Promise<T> {
  const res = await fetch(`${this.cfg.gatewayUrl}${path}`, {
    method: 'GET',
    headers: this.buildHeaders(),
  });
  if (!res.ok) {
    throw new Error(`GET ${path} -> ${res.status}: ${(await res.text()).slice(0, 300)}`);
  }
  return (await res.json()) as T;
}

async post<T>(path: string, body: unknown, extraHeaders?: Record<string, string>): Promise<T> {
  // ... identical with POST + JSON body + extra headers
}

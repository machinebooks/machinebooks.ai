// Extraído de: LibroAIGateway/cap-26-gatewayclient-n7x-mcp.md
async getSpending(): Promise<SpendingSummary> {
  return this.get<SpendingSummary>('/api/v1/spending/me');
}

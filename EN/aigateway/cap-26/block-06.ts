// Extracted from: LibroAIGateway/cap-26-gatewayclient-n7x-mcp.md
async extractText(filePath: string): Promise<string> {
  const buf = await fs.promises.readFile(filePath);
  const form = new FormData();
  form.append('file', new Blob([new Uint8Array(buf)]), path.basename(filePath));
  const headers: Record<string, string> = { Authorization: `Bearer ${this.cfg.bearer}` };
  const res = await fetch(`${this.cfg.gatewayUrl}/api/v1/documents/extract`, {
    method: 'POST', headers, body: form,
  });
  if (!res.ok) throw new Error(`extract -> ${res.status}...`);
  const data = (await res.json()) as { text?: string };
  return data.text ?? '';
}

// Extraído de: LibroAIGateway/cap-26-gatewayclient-n7x-mcp.md
const cfg = loadConfig();
const gw = new GatewayClient(cfg);

const server = new Server(
  { name: 'n7x', version: '0.1.0' },
  { capabilities: { tools: {}, prompts: {} } },
);

// ... handlers ...

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  process.stderr.write(`[n7x-mcp] fatal: ${err.message}\\n`);
  process.exit(1);
});

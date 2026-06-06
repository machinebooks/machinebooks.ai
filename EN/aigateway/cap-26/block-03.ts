// Extracted from: LibroAIGateway/cap-26-gatewayclient-n7x-mcp.md
const raw = await gw.get<unknown>('/api/v1/skills/effective?headless=1');
// Manually filtered: extractEntitledSkills(raw)

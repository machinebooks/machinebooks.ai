// Extraído de: LibroAIGateway/cap-26-gatewayclient-n7x-mcp.md
function outlookUnavailable(r: { error?: string; detail?: string }) {
  if (r.error === 'outlook_unavailable') {
    return {
      content: [{ type: 'text',
        text: 'Outlook no disponible: requiere Windows + Outlook de escritorio + pywin32.' }],
      isError: true,
    };
  }
  return { content: [{ type: 'text', text: `Error: ${r.error || 'fallo desconocido'}` }], isError: true };
}

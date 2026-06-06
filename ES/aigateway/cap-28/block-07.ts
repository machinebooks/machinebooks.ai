// Extraído de: LibroAIGateway/cap-28-admin-operaciones-ia.md
// admin-panel/src/pages/AIPrompts.tsx:28-30 (renderizado de plantillas)
function renderTemplate(content: string, vars: Record<string, string>): string {
  return content.replace(/\{\{\s*([\w.]+)\s*\}\}/g, (_, k) => vars[k] ?? `{{${k}}}`);
}

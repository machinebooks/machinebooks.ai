// Extracted from: LibroAIGateway/cap-28-admin-operations-ai.md
// admin-panel/src/pages/AIPrompts.tsx:28-30 (template rendering)
function renderTemplate(content: string, vars: Record<string, string>): string {
  return content.replace(/\{\{\s*([\w.]+)\s*\}\}/g, (_, k) => vars[k] ?? `{{${k}}}`);
}

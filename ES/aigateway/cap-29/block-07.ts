// Extraído de: LibroAIGateway/cap-29-admin-seguridad-sistema.md
// admin-panel/src/pages/SecurityClassification.tsx (tabs del módulo)
const TABS = ['dashboard', 'incidents', 'patterns', 'eula'] as const;
type Tab = typeof TABS[number];

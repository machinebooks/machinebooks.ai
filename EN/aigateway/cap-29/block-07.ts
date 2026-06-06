// Extracted from: LibroAIGateway/cap-29-admin-security-system.md
// admin-panel/src/pages/SecurityClassification.tsx (module tabs)
const TABS = ['dashboard', 'incidents', 'patterns', 'eula'] as const;
type Tab = typeof TABS[number];

// Extraído de: LibroAIGateway/cap-29-admin-seguridad-sistema.md
// admin-panel/src/pages/SecurityCSE.tsx (tabs del módulo CSE)
const TABS = ['mks', 'breakglass'] as const;

// MasterKeys: lista MEKs activas, crear nueva con Shamir, revocar
// BreakGlass: request 4-eyes, cosign, decrypt, review 72h

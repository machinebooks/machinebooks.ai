// Extracted from: LibroAIGateway/cap-29-admin-security-system.md
// admin-panel/src/pages/SecurityCSE.tsx (CSE module tabs)
const TABS = ['mks', 'breakglass'] as const;

// MasterKeys: list active MEKs, create new with Shamir, revoke
// BreakGlass: request 4-eyes, cosign, decrypt, review 72h

// Extraído de: LibroAIGateway/cap-29-admin-seguridad-sistema.md
// admin-panel/src/pages/Firewall.tsx (acciones disponibles)
type FirewallAction = 'block' | 'warn' | 'redact' | 'allow';

// 'redact' solo tiene efecto en categorías que pasan por la capa PII;
// para el resto (secret/jailbreak) el pipeline solo distingue block vs no-block.
const REDACTABLE = new Set(['pii', 'confidential']);

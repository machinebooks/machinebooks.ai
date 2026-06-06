// Extracted from: LibroAIGateway/cap-29-admin-security-system.md
// admin-panel/src/pages/Firewall.tsx (available actions)
type FirewallAction = 'block' | 'warn' | 'redact' | 'allow';

// 'redact' only takes effect on categories passing through the PII layer;
// for the rest (secret/jailbreak) the pipeline only distinguishes block vs no-block.
const REDACTABLE = new Set(['pii', 'confidential']);

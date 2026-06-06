// Extracted from: LibroAIGateway/cap-29-admin-security-system.md
// admin-panel/src/pages/ApiTokens.tsx
type TokenKind = 'app' | 'user';
type TokenStatus = 'active' | 'suspended' | 'revoked';

interface UnifiedToken {
  id: number;
  kind: TokenKind;
  status: TokenStatus;
  name: string;
  last_used_at: string | null;
  expires_at: string | null;
}

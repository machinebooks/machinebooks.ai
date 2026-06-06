// Extracted from: LibroAIGateway/cap-29-admin-security-system.md
// admin-panel/src/pages/Firewall.tsx (override structure)
interface Override {
  id: number;
  scope_type: 'org' | 'team' | 'user';
  scope_id: number;
  target_type: 'category' | 'guardrail';
  target_key: string;
  action: string;
  note: string | null;
}

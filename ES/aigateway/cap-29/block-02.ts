// Extraído de: LibroAIGateway/cap-29-admin-seguridad-sistema.md
// admin-panel/src/pages/Firewall.tsx (estructura de override)
interface Override {
  id: number;
  scope_type: 'org' | 'team' | 'user';
  scope_id: number;
  target_type: 'category' | 'guardrail';
  target_key: string;
  action: string;
  note: string | null;
}

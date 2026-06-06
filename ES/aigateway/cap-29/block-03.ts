// Extraído de: LibroAIGateway/cap-29-admin-seguridad-sistema.md
// admin-panel/src/pages/Firewall.tsx (normalización de UTC)
function fmtDate(iso: string | null | undefined): string {
  if (!iso) return '—';
  const norm = /[zZ]|[+-]\d{2}:?\d{2}$/.test(iso) ? iso : `${iso}Z`;
  const d = new Date(norm);
  return Number.isNaN(d.getTime()) ? iso : d.toLocaleString();
}

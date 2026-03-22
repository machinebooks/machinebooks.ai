// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// TopologyBuilder.tsx — Tipos de nodo y colores por categoría
interface AssetNodeData {
  label: string;
  type: 'vm' | 'network' | 'firewall' | 'router' | 'switch' | 'storage';
  icon?: string;
  os?: string;
  cpu?: number;
  ram?: number;
  ip?: string;
  status?: string;
}

const nodeColors: Record<string, { bg: string; border: string; icon: string }> = {
  vm:       { bg: '#e3f2fd', border: '#1565c0', icon: '#1565c0' },
  network:  { bg: '#e8f5e9', border: '#2e7d32', icon: '#2e7d32' },
  firewall: { bg: '#fce4ec', border: '#c62828', icon: '#c62828' },
  router:   { bg: '#fff3e0', border: '#e65100', icon: '#e65100' },
  switch:   { bg: '#f3e5f5', border: '#7b1fa2', icon: '#7b1fa2' },
  storage:  { bg: '#e0f2f1', border: '#00695c', icon: '#00695c' },
};

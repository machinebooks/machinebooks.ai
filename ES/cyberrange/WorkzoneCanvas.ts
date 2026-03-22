// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// WorkzoneCanvas.tsx — Interfaz del nodo en el canvas operativo
interface CanvasNode {
  id: string;
  name: string;
  type: 'vm' | 'network' | 'firewall' | 'router';
  x: number;
  y: number;
  // Recursos de la máquina
  cpu?: number;
  memory_mb?: number;
  template?: string;
  // Estado operativo en tiempo real
  status?: 'connected' | 'disconnected' | 'deploying' | 'new';
  power_state?: 'poweredOn' | 'poweredOff' | 'suspended';
  ip_address?: string;
  // Integración con Proxmox
  vmid?: number;
  node_id?: number;
  cluster_id?: number;
  tags?: string[];
  // Operaciones disponibles según el estado actual
  available_operations?: {
    power_on?: boolean;
    power_off?: boolean;
    restart?: boolean;
    connect_console?: boolean;
    get_info?: boolean;
  };
  // Campos para redes como contenedores visuales
  bridge?: string;
  network_cidr?: string;
  gateway?: string;
  size?: { width: number; height: number };
  is_container?: boolean;
}

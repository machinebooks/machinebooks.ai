// Extraído de: LibroCyberrange/cap-13-escenarios-topologias.md
// frontend/src/components/WorkzoneCanvas.tsx — Tipos de nodo del canvas
interface CanvasNode {
  id: string;
  name: string;
  type: 'vm' | 'network' | 'firewall' | 'router';
  x: number;
  y: number;

  // Recursos de la VM
  cpu?: number;
  memory_mb?: number;
  template?: string;           // Template de Proxmox de origen
  os_type?: string;

  // Configuración de red
  vlan_id?: number;
  networks?: string[];         // Redes a las que está conectada
  ip_address?: string;
  bridge?: string;             // Bridge de Proxmox (vmbr0, vmbr1...)
  network_cidr?: string;       // CIDR de la subred

  // Estado en tiempo real (actualizado vía WebSocket)
  status?: 'connected' | 'disconnected' | 'deploying' | 'new';
  power_state?: 'poweredOn' | 'poweredOff' | 'suspended';

  // Identificadores de Proxmox
  vmid?: number;
  node_id?: number;

  // Operaciones disponibles según estado actual
  available_operations?: {
    power_on?: boolean;
    power_off?: boolean;
    restart?: boolean;
    connect_console?: boolean;  // Abrir VNC en navegador
    get_info?: boolean;
  };

  // Contexto de escenario
  deployed?: boolean;
  scenario_id?: number;
  scenario_machine_name?: string;

  // Redes como contenedores visuales
  is_container?: boolean;       // Las redes son rectángulos contenedores
  size?: { width: number; height: number };
  vm_count?: number;
  description?: string;
}

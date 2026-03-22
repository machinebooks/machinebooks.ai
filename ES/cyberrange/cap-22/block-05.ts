// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// Biblioteca de activos para arrastrar al canvas
const defaultAssets: AssetTemplate[] = [
  // Servidores
  { id: 'ubuntu-server', label: 'Ubuntu Server', type: 'vm',
    category: 'Servers', os: 'Ubuntu 22.04', cpu: 2, ram: 4096 },
  { id: 'windows-server', label: 'Windows Server', type: 'vm',
    category: 'Servers', os: 'Windows Server 2022', cpu: 4, ram: 8192 },
  // Estaciones de ataque
  { id: 'kali', label: 'Kali Linux', type: 'vm',
    category: 'Workstations', os: 'Kali 2024', cpu: 4, ram: 8192 },
  { id: 'parrot', label: 'Parrot OS', type: 'vm',
    category: 'Workstations', os: 'Parrot Security', cpu: 2, ram: 4096 },
  // Segmentos de red
  { id: 'lan', label: 'LAN Network', type: 'network', category: 'Network' },
  { id: 'dmz', label: 'DMZ', type: 'network', category: 'Network' },
  // Seguridad perimetral
  { id: 'pfsense', label: 'pfSense', type: 'firewall',
    category: 'Security', os: 'pfSense CE', cpu: 1, ram: 2048 },
  // OT/IoT — escenarios de infraestructura crítica
  { id: 'plc-modbus', label: 'PLC Modbus', type: 'vm',
    category: 'OT/IoT', os: 'Modbus TCP', cpu: 1, ram: 512 },
  { id: 'scada', label: 'SCADA Server', type: 'vm',
    category: 'OT/IoT', os: 'SCADA Linux', cpu: 2, ram: 4096 },
];

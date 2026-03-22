// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// MachineContext.tsx — Estado centralizado de infraestructura
interface MachineState {
  clusters: ProxmoxCluster[];
  vms: ProxmoxVM[];
  workzoneVMs: ProxmoxVM[];      // VMs del workzone activo
  templates: ProxmoxTemplate[];
  stats: DashboardStats | null;
  loading: boolean;
  error: string | null;
  lastUpdate: number;
  proxmoxConfig: {
    default_host: string;
    default_port: number;
    ssl_verify: boolean;
    console_base_url: string;
  } | null;
}

type MachineAction =
  | { type: 'SET_LOADING'; loading: boolean }
  | { type: 'SET_ERROR'; error: string | null }
  | { type: 'SET_CLUSTERS'; clusters: ProxmoxCluster[] }
  | { type: 'SET_VMS'; vms: ProxmoxVM[] }
  | { type: 'SET_WORKZONE_VMS'; vms: ProxmoxVM[] }
  | { type: 'SET_TEMPLATES'; templates: ProxmoxTemplate[] }
  | { type: 'SET_STATS'; stats: DashboardStats | null }
  | { type: 'UPDATE_VM'; vm: ProxmoxVM }
  | { type: 'REMOVE_VM'; vmId: number }
  | { type: 'ADD_VM'; vm: ProxmoxVM }
  | { type: 'SET_PROXMOX_CONFIG'; config: any }
  | { type: 'SET_LAST_UPDATE' };

function machineReducer(
  state: MachineState, action: MachineAction
): MachineState {
  switch (action.type) {
    case 'SET_VMS':
      return {
        ...state,
        vms: Array.isArray(action.vms) ? action.vms : [],
        lastUpdate: Date.now()
      };
    case 'UPDATE_VM':
      return {
        ...state,
        vms: state.vms.map(vm =>
          vm.id === action.vm.id ? action.vm : vm
        ),
        lastUpdate: Date.now()
      };
    case 'SET_WORKZONE_VMS':
      return {
        ...state,
        workzoneVMs: Array.isArray(action.vms) ? action.vms : [],
        lastUpdate: Date.now()
      };
    // ... más cases para cada tipo de acción
    default:
      return state;
  }
}

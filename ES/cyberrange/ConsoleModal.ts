// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// ConsoleModal.tsx — Modal de consola con soporte dual
interface ConsoleModalProps {
  vm: ProxmoxVM | null;
  isOpen: boolean;
  onClose: () => void;
  onGetConsoleUrl: (
    vmId: number,
    consoleType?: 'terminal' | 'novnc'
  ) => Promise<{
    success: boolean;
    urls: {
      primary: string;
      webshell?: string;
      terminal?: string;
      websocket?: string;
      novnc?: string;
    };
    console_type: string;
    iframe_compatible?: boolean;
    credentials?: {
      vnc_user?: string;
      vnc_password?: string;
      vnc_ticket?: string;
      pve_auth_cookie?: string;
      csrf_token?: string;
    };
  }>;
}

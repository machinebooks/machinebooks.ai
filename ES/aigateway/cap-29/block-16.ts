// Extraído de: LibroAIGateway/cap-29-admin-seguridad-sistema.md
// admin-panel/src/pages/EmailSmtp.tsx (campos del formulario)
interface FormState {
  host: string;
  port: number;
  tls: boolean;
  username: string;
  password: string;
  from_email: string;
  from_name: string;
}

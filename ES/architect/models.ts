// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// models.ts — Tipos compartidos que reflejan los modelos de respuesta del backend
// Estos tipos son la fuente de verdad del contrato de API en el frontend

// ---- Autenticación ----
export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  expires_in: number;          // segundos hasta que expira el access_token
  user: UserProfile;
}

export interface UserProfile {
  id: number;
  email: string;
  full_name: string;
  current_app: AppName;
  role: UserRole;
  permissions: ModulePermissions;
  ai_modules_access: AIModule[];
  last_login: string;          // ISO 8601
}

export type AppName = 'operations' | 'analytics' | 'admin';
export type UserRole = 'admin' | 'manager' | 'analyst' | 'viewer';
export type AIModule = 'copilot' | 'document_analysis' | 'reporting';

export type ModulePermissions = {
  [module: string]: Array<'read' | 'write' | 'delete' | 'export'>;
};


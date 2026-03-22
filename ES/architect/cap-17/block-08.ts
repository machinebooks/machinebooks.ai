// Extraído de: LibroTecnico/cap-17-integracion-frontend-backend.md
// ---- Respuesta paginada (patrón reutilizable) ----
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// ---- Respuesta de error estándar del backend ----
export interface ApiError {
  error: string;               // código de error legible por máquina
  message: string;             // mensaje legible por humanos
  details?: Record<string, string[]>;  // errores de validación por campo
  request_id?: string;         // ID de correlación para trazabilidad en logs
}

// ---- Operaciones (módulo principal) ----
export interface Operation {
  id: number;
  reference: string;
  title: string;
  status: OperationStatus;
  assigned_to: number | null;
  created_at: string;
  updated_at: string;
  metadata: OperationMetadata;
}

export type OperationStatus =
  | 'draft'
  | 'active'
  | 'review'
  | 'approved'
  | 'closed';

export interface OperationMetadata {
  category: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  estimated_value: number | null;
  tags: string[];
}

// ---- Respuesta de stream SSE ----
export interface StreamChunk {
  text: string;
  model: string;
  usage?: {
    input_tokens: number;
    output_tokens: number;
  };
}

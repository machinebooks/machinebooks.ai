// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// ChallengeWorkspace.tsx — Estructura del workspace de resolución
interface ChallengeWorkspaceType {
  id: number;
  title: string;
  type: string;                // 'ctf' | 'crisis' | 'guided' | 'escape'
  description: string;
  instructions?: string;
  max_points: number;
  bonus_points?: number;       // Puntos extra por velocidad
  skills: string[];            // ['Web Security', 'SQL Injection']
  mitre_tactics: string[];     // ['T1190', 'T1059']
  mitre_techniques: MitreTechniqueData[];
  flags_count: number;
  hints_available: number;
  difficulty: string;
  files: ChallengeFile[];      // Ficheros descargables
  flags: FlagInfo[];           // Flags del challenge
  user_instance?: {
    status: string;
    started_at?: string;
    completed_at?: string;
    points: number;
    flags_completed: number;
  };
  environment?: {
    type: string;
    url?: string;              // URL de la consola/entorno
    status: string;
  };
}

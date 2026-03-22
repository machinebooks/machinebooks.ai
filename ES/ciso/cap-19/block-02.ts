// Extraído de: LibroCISO/cap-19-dashboards-copiloto.md
// Ejemplo didáctico: columnas de dominio GRC para tabla de tratamientos
import { ColumnDef } from "@tanstack/react-table";

interface Treatment {
  id: number;
  name: string;
  legal_basis: string;
  data_categories: string[];
  dpia_status: "not_required" | "pending" | "in_progress" | "completed";
  last_review: string;
}

/** Columnas con semántica regulatoria — lo que diferencia un GRC de un CRUD */
const treatmentColumns: ColumnDef<Treatment>[] = [
  { accessorKey: "name", header: "Tratamiento", size: 250 },
  {
    accessorKey: "legal_basis",
    header: "Base jurídica",
    // Badge de color: el DPO identifica de un vistazo los tratamientos
    // basados en consentimiento (que requieren renovación periódica)
    cell: ({ getValue }) => (
      <span className="rounded bg-blue-50 px-2 py-1 text-xs text-blue-700">
        {getValue<string>()}
      </span>
    ),
  },
  {
    accessorKey: "dpia_status",
    header: "DPIA",
    // Semáforo regulatorio: rojo = pendiente (riesgo de incumplimiento Art. 35),
    // amarillo = en progreso, verde = completada, gris = no requerida
    cell: ({ getValue }) => {
      const status = getValue<string>();
      const colors: Record<string, string> = {
        completed: "bg-green-100 text-green-800",
        in_progress: "bg-yellow-100 text-yellow-800",
        pending: "bg-red-100 text-red-800",
        not_required: "bg-gray-100 text-gray-500",
      };
      return (
        <span className={`rounded px-2 py-1 text-xs ${colors[status]}`}>
          {status === "not_required" ? "No requerida" : status}
        </span>
      );
    },
  },
  { accessorKey: "last_review", header: "Última revisión", size: 130 },
];

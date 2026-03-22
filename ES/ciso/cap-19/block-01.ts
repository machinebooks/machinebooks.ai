// Extraído de: LibroCISO/cap-19-dashboards-copiloto.md
// Ejemplo didáctico: radar de cumplimiento con Recharts
import {
  RadarChart, PolarGrid, PolarAngleAxis,
  PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip,
} from "recharts";

interface FrameworkCompliance {
  framework: string;    // "ENS", "ISO 27001", "NIS2"...
  compliance: number;   // 0-100, porcentaje de controles evaluados
  target: number;       // 0-100, objetivo para el periodo
}

function ComplianceRadar({ data }: { data: FrameworkCompliance[] }) {
  return (
    <ResponsiveContainer width="100%" height={360}>
      <RadarChart data={data} cx="50%" cy="50%" outerRadius="75%">
        <PolarGrid strokeDasharray="3 3" />
        <PolarAngleAxis
          dataKey="framework"
          tick={{ fontSize: 12, fill: "#64748b" }}
        />
        <PolarRadiusAxis angle={30} domain={[0, 100]} />

        {/* Objetivo: línea punteada */}
        <Radar
          name="Objetivo"
          dataKey="target"
          stroke="#94a3b8"
          fill="none"
          strokeDasharray="5 5"
        />

        {/* Estado actual: área con relleno */}
        <Radar
          name="Cumplimiento actual"
          dataKey="compliance"
          stroke="#3b82f6"
          fill="#3b82f6"
          fillOpacity={0.25}
        />

        <Tooltip
          formatter={(value: number) => `${value}%`}
          contentStyle={{ backgroundColor: "#1e293b", border: "none" }}
          labelStyle={{ color: "#f8fafc" }}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}

// Extraído de: LibroFinOps/cap-23-coste-equipo.md
// components/TCOBreakdownChart.tsx
// Visualización del desglose de TCO con énfasis en la proporción personas/tecnología.
// Usa Recharts para el gráfico de anillo y la tabla de desglose por perfil.

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

interface TCOData {
  personas_eur: number;
  tokens_eur: number;
  cloud_eur: number;
  herramientas_eur: number;
  desglose_por_perfil: Record<string, number>;
}

const COLORS = ["#ef4444", "#3b82f6", "#22c55e", "#f59e0b"];

export function TCOBreakdownChart({ data }: { data: TCOData }) {
  const total = data.personas_eur + data.tokens_eur + data.cloud_eur + data.herramientas_eur;
  const pctPersonas = ((data.personas_eur / total) * 100).toFixed(1);

  const chartData = [
    { name: "Personas", value: data.personas_eur },
    { name: "Cloud", value: data.cloud_eur },
    { name: "Tokens IA", value: data.tokens_eur },
    { name: "Herramientas", value: data.herramientas_eur },
  ];

  return (
    <div className="grid grid-cols-2 gap-6">
      <div className="relative">
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie data={chartData} innerRadius={60} outerRadius={100} dataKey="value">
              {chartData.map((_, i) => (
                <Cell key={i} fill={COLORS[i]} />
              ))}
            </Pie>
            <Tooltip formatter={(v: number) => `€${v.toLocaleString("es-ES")}`} />
          </PieChart>
        </ResponsiveContainer>
        {/* Indicador central: % personas */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-red-600">{pctPersonas}%</span>
        </div>
      </div>
      {/* Tabla de desglose por perfil */}
      <div className="space-y-2">
        <h4 className="font-semibold text-sm text-gray-600">Desglose por perfil</h4>
        {Object.entries(data.desglose_por_perfil).map(([perfil, coste]) => (
          <div key={perfil} className="flex justify-between text-sm">
            <span>{perfil}</span>
            <span className="font-mono">€{coste.toLocaleString("es-ES")}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

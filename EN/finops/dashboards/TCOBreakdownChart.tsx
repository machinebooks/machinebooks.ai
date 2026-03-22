// Source: The FinOps Engineer and the Machine -- Chapter 23
// Pattern: TCO breakdown chart React component

// components/TCOBreakdownChart.tsx
// TCO breakdown visualization with emphasis on the people/technology proportion.
// Uses Recharts for the donut chart and the profile breakdown table.

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
    { name: "People", value: data.personas_eur },
    { name: "Cloud", value: data.cloud_eur },
    { name: "AI Tokens", value: data.tokens_eur },
    { name: "Tools", value: data.herramientas_eur },
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
            <Tooltip formatter={(v: number) => `EUR${v.toLocaleString("en-US")}`} />
          </PieChart>
        </ResponsiveContainer>
        {/* Central indicator: % people */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-red-600">{pctPersonas}%</span>
        </div>
      </div>
      {/* Profile breakdown table */}
      <div className="space-y-2">
        <h4 className="font-semibold text-sm text-gray-600">Breakdown by profile</h4>
        {Object.entries(data.desglose_por_perfil).map(([perfil, coste]) => (
          <div key={perfil} className="flex justify-between text-sm">
            <span>{perfil}</span>
            <span className="font-mono">EUR{coste.toLocaleString("en-US")}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

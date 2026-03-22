// Extraído de: LibroFinOps/cap-19-unit-economics.md
// components/UnitEconomicsDashboard.tsx
import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

interface UnitEconomicsData {
  users: { total_active: number; distribution_by_profile: Record<string, number> };
  costs: { avg_per_active_user_usd: number; by_profile_usd: Record<string, number>;
           marginal_new_user_usd: number };
  saas_metrics: { break_even_tenants: number; infra_base_eur: number };
}

export function UnitEconomicsDashboard() {
  const [data, setData] = useState<UnitEconomicsData | null>(null);
  useEffect(() => {
    fetch("/api/v1/unit-economics?days=30").then((r) => r.json()).then(setData);
  }, []);

  if (!data) return <div>Cargando...</div>;

  const chartData = ["power", "average", "light"].map((p) => ({
    profile: p.charAt(0).toUpperCase() + p.slice(1),
    usuarios: data.users.distribution_by_profile[p] || 0,
    coste: data.costs.by_profile_usd[p] || 0,
  }));

  return (
    <div className="space-y-6 p-6">
      <div className="grid grid-cols-3 gap-4">
        <MetricCard label="Coste por MAU"
          value={`$${data.costs.avg_per_active_user_usd.toFixed(2)}`} />
        <MetricCard label="Coste marginal"
          value={`$${data.costs.marginal_new_user_usd.toFixed(2)}`} />
        <MetricCard label="Break-even"
          value={`${data.saas_metrics.break_even_tenants} clientes`} />
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={chartData}>
          <XAxis dataKey="profile" /><YAxis /><Tooltip />
          <Bar dataKey="usuarios" fill="#6366f1" />
          <Bar dataKey="coste" fill="#f59e0b" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

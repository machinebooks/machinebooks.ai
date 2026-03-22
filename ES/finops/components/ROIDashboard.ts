// Extraído de: LibroFinOps/cap-17-roi-humanbaseline.md
// components/ROIDashboard.tsx — Vista ejecutiva del ROI
interface ROISummary {
  period_days: number;
  total_tasks: number;
  acceptance_rate: number;
  total_llm_cost_eur: number;
  total_value_eur: number;
  roi_global: number;
  net_value_eur: number;
  by_task_type: Record<string, {
    count: number; roi: number; llm_cost: number; value: number;
  }>;
}

export function ROIDashboard({ tenantId }: { tenantId?: number }) {
  const [summary, setSummary] = useState<ROISummary | null>(null);

  useEffect(() => {
    const params = tenantId ? `?days=30&tenant_id=${tenantId}` : "?days=30";
    fetch(`/api/v1/roi/summary${params}`)
      .then((r) => r.json())
      .then(setSummary);
  }, [tenantId]);

  if (!summary) return <div className="text-gray-500">Cargando...</div>;

  const taskData = Object.entries(summary.by_task_type)
    .map(([type, d]) => ({ type, roi: d.roi, coste: d.llm_cost, valor: d.value }))
    .sort((a, b) => b.roi - a.roi);

  return (
    <div className="grid grid-cols-2 gap-6 p-6">
      <div className="col-span-2 grid grid-cols-4 gap-4">
        <KPICard label="ROI global" value={`${summary.roi_global}:1`} />
        <KPICard label="Valor neto" value={`€${summary.net_value_eur.toLocaleString("es-ES")}`} />
        <KPICard label="Aceptación" value={`${(summary.acceptance_rate * 100).toFixed(1)}%`} />
        <KPICard label="Coste LLM" value={`€${summary.total_llm_cost_eur.toFixed(2)}`} />
      </div>
      <div className="bg-white rounded-lg p-4 shadow">
        <h3 className="text-sm font-medium text-gray-700 mb-3">
          ROI por tipo de tarea (últimos {summary.period_days} días)
        </h3>
        {taskData.map((t) => (
          <div key={t.type} className="flex items-center justify-between py-1">
            <span className="text-sm text-gray-600">{t.type.replace(/_/g, " ")}</span>
            <span className={`text-sm font-semibold ${t.roi > 0 ? "text-green-600" : "text-red-600"}`}>
              {t.roi > 0 ? `${t.roi}:1` : "Negativo"}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

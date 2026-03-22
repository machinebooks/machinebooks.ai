// Extraído de: LibroFinOps/cap-07-dashboards.md
// components/AIMetricsTab.tsx — Vista del CFO
const CFOView = () => {
  const [data, setData] = useState<CFOMetrics | null>(null);

  useEffect(() => {
    fetch("/api/dashboard/cfo?months=6")
      .then((r) => r.json())
      .then(setData);
  }, []);

  if (!data) return <p className="text-gray-400">Cargando...</p>;

  const budget = 450; // € mensuales, configurable
  const current = data.monthly_trend.at(-1)?.cost_eur ?? 0;
  const status =
    current >= budget ? "alert"
    : current >= budget * 0.8 ? "warning"
    : "ok";

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <KPICard
          label="Gasto IA este mes"
          value={`€${current.toFixed(0)}`}
          status={status}
        />
        <KPICard
          label="Proyección fin de mes"
          value={`€${data.projection_eur?.toFixed(0) ?? "—"}`}
          status={
            (data.projection_eur ?? 0) > budget
              ? "warning" : "ok"
          }
        />
        <KPICard label="Presupuesto" value={`€${budget}`} />
        <KPICard
          label="Media 6 meses"
          value={`€${data.summary.avg_monthly_eur.toFixed(0)}`}
        />
      </div>

      {/* Gráfico de tendencia con línea de presupuesto */}
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data.monthly_trend}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} unit="€" />
          <Tooltip
            formatter={(v: number) => [`€${v.toFixed(2)}`, "Coste"]}
          />
          <Line
            type="monotone" dataKey="cost_eur"
            stroke="#6366f1" strokeWidth={2} name="Gasto IA"
          />
          <Legend />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

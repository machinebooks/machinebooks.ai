// Source: The FinOps Engineer and the Machine -- Chapter 7
// Pattern: React KPI card component for AI metrics

// components/AIMetricsTab.tsx — CFO view
const CFOView = () => {
  const [data, setData] = useState<CFOMetrics | null>(null);

  useEffect(() => {
    fetch("/api/dashboard/cfo?months=6")
      .then((r) => r.json())
      .then(setData);
  }, []);

  if (!data) return <p className="text-gray-400">Loading...</p>;

  const budget = 450; // € monthly, configurable
  const current = data.monthly_trend.at(-1)?.cost_eur ?? 0;
  const status =
    current >= budget ? "alert"
    : current >= budget * 0.8 ? "warning"
    : "ok";

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <KPICard
          label="AI spend this month"
          value={`€${current.toFixed(0)}`}
          status={status}
        />
        <KPICard
          label="End-of-month projection"
          value={`€${data.projection_eur?.toFixed(0) ?? "—"}`}
          status={
            (data.projection_eur ?? 0) > budget
              ? "warning" : "ok"
          }
        />
        <KPICard label="Budget" value={`€${budget}`} />
        <KPICard
          label="6-month average"
          value={`€${data.summary.avg_monthly_eur.toFixed(0)}`}
        />
      </div>

      {/* Trend chart with budget line */}
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data.monthly_trend}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} unit="€" />
          <Tooltip
            formatter={(v: number) => [`€${v.toFixed(2)}`, "Cost"]}
          />
          <Line
            type="monotone" dataKey="cost_eur"
            stroke="#6366f1" strokeWidth={2} name="AI Spend"
          />
          <Legend />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

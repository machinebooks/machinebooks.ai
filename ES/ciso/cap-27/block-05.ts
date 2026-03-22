// Extraído de: LibroCISO/cap-27-executive-dashboard.md
export default function ExecutiveDashboardPage() {
  const { data: d, isLoading } = useQuery<ExecutiveDashboard>({
    queryKey: ['executive-dashboard'],
    queryFn: executiveApi.getDashboard,
  })

  if (isLoading) return <LoadingSkeleton />
  if (!d) return <EmptyState />

  const varColor = d.cyber_risk.cyber_var_95_eur > 5e6
    ? 'text-red-600'
    : d.cyber_risk.cyber_var_95_eur > 1e6
      ? 'text-orange-600'
      : 'text-green-600'

  return (
    <div className="space-y-6">
      {/* Banda 1: Score global + KPIs destacados */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <ScoreGauge score={d.overall_grc_score} label="GRC Score" />
        <KPI label="Cyber VaR (95%)"
          value={`${fmt(d.cyber_risk.cyber_var_95_eur)} EUR`}
          color={varColor} />
        <KPI label="NIS2 Compliance"
          value={`${d.nis2.compliance_score}%`}
          sub={`${d.nis2.compliant}/${d.nis2.total_requirements}`} />
        <KPI label="Proveedores"
          value={d.tprm.total_suppliers}
          sub={`${d.tprm.critical_suppliers} críticos`} />
        <KPI label="Click rate phishing"
          value={d.policy_awareness.avg_phishing_click_rate
            ? `${d.policy_awareness.avg_phishing_click_rate}%`
            : 'N/A'} />
      </div>

      {/* Banda 2: Tarjetas por módulo */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <ModuleCard title="Third-Party Risk" accent="border-l-blue-500">
          <Metric label="Score medio"
            value={d.tprm.avg_supplier_score
              ? `${d.tprm.avg_supplier_score}/100` : 'N/A'} />
          <Metric label="Hallazgos abiertos"
            value={d.tprm.open_findings} />
        </ModuleCard>
        {/* NIS2, DORA, Cyber Risk, Policy, AI Gov... */}
      </div>

      {/* Banda 3: Frameworks de compliance */}
      <ComplianceFrameworksBand frameworks={d.compliance_frameworks} />
    </div>
  )
}

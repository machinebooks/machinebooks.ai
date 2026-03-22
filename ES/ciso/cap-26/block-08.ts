// Extraído de: LibroCISO/cap-26-politicas-concienciacion.md
// Vista de dashboard con KPIs cruzados
function DashboardTab({ data }: { data: PolicyAwarenessDashboard }) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KPI
          label="Políticas publicadas"
          value={`${data.policies_by_status?.published || 0}/${data.total_policies}`}
        />
        <KPI
          label="Campañas activas"
          value={data.active_campaigns}
          color="text-green-600"
        />
        <KPI
          label="Simulaciones phishing"
          value={data.total_phishing_simulations}
        />
        <KPI
          label="Click rate medio"
          value={
            data.avg_phishing_click_rate != null
              ? `${data.avg_phishing_click_rate}%`
              : 'N/A'
          }
          color={
            data.avg_phishing_click_rate && data.avg_phishing_click_rate > 10
              ? 'text-red-600'
              : 'text-green-600'
          }
        />
      </div>
    </div>
  )
}

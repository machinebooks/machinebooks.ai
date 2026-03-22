// Extraído de: LibroCISO/cap-27-executive-dashboard.md
function KPI({ label, value, sub, color = 'text-gray-900' }: {
  label: string
  value: string | number
  sub?: string
  color?: string
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <p className="text-[10px] font-semibold text-gray-400
        uppercase tracking-wider">{label}</p>
      <p className={`text-xl font-bold mt-1 ${color}`}>{value}</p>
      {sub && (
        <p className="text-[10px] text-gray-400 mt-0.5">{sub}</p>
      )}
    </div>
  )
}

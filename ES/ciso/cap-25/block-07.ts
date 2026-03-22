// Extraído de: LibroCISO/cap-25-vigilancia-normativa.md
// Mapas de color para estados y severidades
const statusColors: Record<string, string> = {
  new: 'bg-blue-100 text-blue-800',
  analyzing: 'bg-yellow-100 text-yellow-800',
  analyzed: 'bg-green-100 text-green-800',
  dismissed: 'bg-gray-100 text-gray-500',
  requires_action: 'bg-red-100 text-red-800',
}

const severityColors: Record<string, string> = {
  info: 'bg-blue-100 text-blue-800',
  warning: 'bg-yellow-100 text-yellow-800',
  critical: 'bg-red-100 text-red-800',
}

function KPICard({ label, value, color }: {
  label: string; value: string | number; color?: string
}) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5">
      <p className="text-xs font-medium text-gray-500 uppercase">
        {label}
      </p>
      <p className={`text-2xl font-bold mt-1 ${color}`}>
        {value}
      </p>
    </div>
  )
}

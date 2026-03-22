// Extraído de: LibroCISO/cap-27-executive-dashboard.md
function ModuleCard({ title, children, accent }: {
  title: string
  children: React.ReactNode
  accent?: string  // "border-l-blue-500", "border-l-red-500", etc.
}) {
  return (
    <div className={`bg-white rounded-xl border border-gray-200
      border-l-4 ${accent} p-5`}>
      <h3 className="text-sm font-bold text-gray-700 mb-3
        uppercase tracking-wider">{title}</h3>
      {children}
    </div>
  )
}

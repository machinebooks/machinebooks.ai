// Extraído de: LibroCISO/cap-27-executive-dashboard.md
// Gauge circular para el GRC Score global
function ScoreGauge({ score, label }: {
  score: number | null; label: string
}) {
  const s = score ?? 0
  // Color semafórico: verde > 80, amarillo > 60, rojo < 40
  const color = s >= 80
    ? 'text-green-600'
    : s >= 60
      ? 'text-yellow-600'
      : s >= 40
        ? 'text-orange-600'
        : 'text-red-600'

  return (
    <div className="text-center">
      <div className="relative w-24 h-24 mx-auto">
        <svg className="w-24 h-24 -rotate-90" viewBox="0 0 100 100">
          {/* Fondo gris */}
          <circle cx="50" cy="50" r="42" fill="none"
            stroke="#e5e7eb" strokeWidth="8" />
          {/* Arco de progreso */}
          <circle cx="50" cy="50" r="42" fill="none"
            stroke="currentColor" className={color}
            strokeWidth="8" strokeLinecap="round"
            strokeDasharray={`${s * 2.64} 264`} />
        </svg>
        <span className={`absolute inset-0 flex items-center
          justify-center text-2xl font-bold ${color}`}>
          {score != null ? Math.round(s) : '-'}
        </span>
      </div>
      <p className="text-xs text-gray-500 mt-2">{label}</p>
    </div>
  )
}

// Extraído de: LibroTecnico/cap-16-react-ia.md
// Gráfico con manejo explícito de datos ausentes
// Este patrón requirió varias iteraciones de corrección manual
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts'

interface DataPoint {
  date: string
  value: number | null     // null para gaps en la serie
  target?: number
}

// Claude generó inicialmente connectNulls={true}, que dibujaba
// líneas atravesando gaps vacíos — incorrecto visualmente
// La corrección: connectNulls={false} y manejo explícito de gaps
export function TimeSeriesChart({ data, title }: {
  data: DataPoint[]
  title: string
}) {
  // Formateo de fecha para el eje X: "mar 2025"
  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr)
    return d.toLocaleDateString('es-ES', { month: 'short', year: '2-digit' })
  }

  const formatValue = (value: number) =>
    new Intl.NumberFormat('es-ES', {
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(value)

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <h3 className="mb-4 text-sm font-medium text-gray-700">{title}</h3>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={data} margin={{ top: 4, right: 16, left: 0, bottom: 4 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="date"
            tickFormatter={formatDate}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            tickFormatter={formatValue}
            tick={{ fontSize: 11 }}
            width={48}
          />
          <Tooltip
            formatter={(value: number | null) =>
              value !== null ? formatValue(value) : 'Sin datos'
            }
            labelFormatter={formatDate}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
            connectNulls={false}   // Corrección manual: no conectar gaps
          />
          {/* Línea de target si existe */}
          {data.some(d => d.target !== undefined) && (
            <Line
              type="monotone"
              dataKey="target"
              stroke="#e5e7eb"
              strokeWidth={1}
              strokeDasharray="4 4"
              dot={false}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

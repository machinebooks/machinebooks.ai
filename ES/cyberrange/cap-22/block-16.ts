// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// Ejemplo de gráfico Recharts para métricas de clúster
import {
  LineChart, Line, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';

interface ClusterMetricsChartProps {
  data: Array<{
    timestamp: string;
    cpu: number;
    memory: number;
    vms: number;
  }>;
}

const ClusterMetricsChart: React.FC<ClusterMetricsChartProps> = ({
  data
}) => (
  <ResponsiveContainer width="100%" height={300}>
    <LineChart data={data}
      margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
      <XAxis dataKey="timestamp" stroke="#9ca3af"
        tickFormatter={(ts) =>
          new Date(ts).toLocaleTimeString('es-ES', {
            hour: '2-digit', minute: '2-digit'
          })
        } />
      <YAxis stroke="#9ca3af" domain={[0, 100]} />
      <Tooltip contentStyle={{
        backgroundColor: '#1f2937', border: 'none'
      }} />
      <Line type="monotone" dataKey="cpu"
        stroke="#3b82f6" name="CPU %" dot={false} />
      <Line type="monotone" dataKey="memory"
        stroke="#10b981" name="RAM %" dot={false} />
    </LineChart>
  </ResponsiveContainer>
);

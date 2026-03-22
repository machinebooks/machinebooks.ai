// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// ClusterDashboard.tsx — Estado del clúster Proxmox
interface ClusterDashboardProps {
  stats: DashboardStats | null;
  loading: boolean;
  onRefresh: () => void;
}

const ClusterDashboard: React.FC<ClusterDashboardProps> = ({
  stats, loading, onRefresh
}) => {
  const { t } = useTranslation();

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="text-green-500" />;
      case 'offline':
        return <XCircle className="text-red-500" />;
      case 'maintenance':
        return <AlertTriangle className="text-yellow-500" />;
      default:
        return <XCircle className="text-gray-500" />;
    }
  };

  const formatBytes = (bytes: number): string => {
    const gb = bytes / (1024 * 1024 * 1024);
    return `${gb.toFixed(1)} GB`;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
      <MetricCard icon={<Server />}
        label={t('clusterDashboard.totalNodes')}
        value={stats?.total_nodes} />
      <MetricCard icon={<Cpu />}
        label={t('clusterDashboard.cpuUsage')}
        value={`${stats?.cpu_usage?.toFixed(1)}%`} />
      <MetricCard icon={<MemoryStick />}
        label={t('clusterDashboard.memoryUsed')}
        value={formatBytes(stats?.memory_used || 0)} />
      <MetricCard icon={<HardDrive />}
        label={t('clusterDashboard.storageUsed')}
        value={formatBytes(stats?.storage_used || 0)} />
    </div>
  );
};

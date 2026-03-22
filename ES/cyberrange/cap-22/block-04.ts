// Extraído de: LibroCyberrange/cap-22-react-frontend.md
// AssetNode — Componente de nodo personalizado para ReactFlow
const AssetNode: React.FC<{ data: AssetNodeData; selected: boolean }> = ({
  data, selected
}) => {
  const colors = nodeColors[data.type] || nodeColors.vm;

  return (
    <div style={{
      background: colors.bg,
      border: `2px solid ${selected ? '#ff9800' : colors.border}`,
      borderRadius: '10px',
      padding: '12px 16px',
      minWidth: '140px',
      boxShadow: selected
        ? '0 0 0 2px #ff9800'
        : '0 2px 6px rgba(0,0,0,0.1)',
      cursor: 'grab',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ color: colors.icon }}>{nodeIcons[data.type]}</span>
        <span style={{ fontWeight: 600, fontSize: '13px' }}>{data.label}</span>
      </div>
      {data.os && (
        <div style={{ fontSize: '11px', color: '#666' }}>{data.os}</div>
      )}
      {(data.cpu || data.ram) && (
        <div style={{ fontSize: '10px', color: '#999', marginTop: '2px' }}>
          {data.cpu && <span>{data.cpu}vCPU </span>}
          {data.ram && <span>{data.ram}MB</span>}
        </div>
      )}
      {data.ip && (
        <div style={{
          fontSize: '10px', color: colors.icon, fontFamily: 'monospace'
        }}>
          {data.ip}
        </div>
      )}
    </div>
  );
};

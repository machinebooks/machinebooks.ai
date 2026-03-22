// Extraído de: LibroTecnico/cap-23-inteligencia-comercial.md
interface HeatmapCell {
  sectorId: number;
  sectorName: string;
  serviceLineId: number;
  serviceLineName: string;
  totalScore: number;
  scoreDemand: number;
  scoreTraction: number;
  scoreEconomic: number;
  scoreRightToWin: number;
}

// Función de interpolación de color: 0=rojo, 50=amarillo, 100=verde
function scoreToColor(score: number): string {
  if (score < 33) {
    const t = score / 33;
    const r = 220;
    const g = Math.round(t * 160);
    return `rgb(${r},${g},40)`;
  } else if (score < 66) {
    const t = (score - 33) / 33;
    const r = Math.round(220 - t * 100);
    const g = 160;
    return `rgb(${r},${g},40)`;
  } else {
    const t = (score - 66) / 34;
    const g = Math.round(160 + t * 60);
    return `rgb(40,${g},60)`;
  }
}

const HeatmapCell: React.FC<{ cell: HeatmapCell }> = ({ cell }) => {
  const [showDetail, setShowDetail] = useState(false);

  return (
    <div
      className="relative cursor-pointer border border-gray-200 rounded"
      style={{ backgroundColor: scoreToColor(cell.totalScore) }}
      onMouseEnter={() => setShowDetail(true)}
      onMouseLeave={() => setShowDetail(false)}
    >
      {/* Score principal */}
      <span className="font-bold text-white text-sm">
        {cell.totalScore.toFixed(0)}
      </span>

      {/* Tooltip con subscores — solo en hover */}
      {showDetail && (
        <div className="absolute z-50 bg-gray-900 text-white p-3 rounded shadow-lg
                        text-xs w-48 -translate-x-1/2 left-1/2 bottom-full mb-1">
          <div className="font-semibold mb-1">
            {cell.sectorName} × {cell.serviceLineName}
          </div>
          <div className="space-y-1">
            <div>Demanda (30%): {cell.scoreDemand.toFixed(0)}</div>
            <div>Tracción (20%): {cell.scoreTraction.toFixed(0)}</div>
            <div>Económico (25%): {cell.scoreEconomic.toFixed(0)}</div>
            <div>RTW (25%): {cell.scoreRightToWin.toFixed(0)}</div>
          </div>
        </div>
      )}
    </div>
  );
};

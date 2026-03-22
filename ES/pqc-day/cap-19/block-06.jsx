// Extraído de: LibroPQC/cap-19-dashboard.md
const PQCScoreGauge = ({ score }) => {
  const getColor = (s) => {
    if (s >= 80) return '#4caf50'  // Verde — excelente
    if (s >= 50) return '#ff9800'  // Naranja — atención
    return '#f44336'               // Rojo — crítico
  }

  return (
    <Box sx={{ textAlign: 'center' }}>
      <Box sx={{ position: 'relative', display: 'inline-flex' }}>
        {/* Fondo gris del indicador circular */}
        <CircularProgress
          variant="determinate"
          value={100}
          size={120}
          thickness={4}
          sx={{ color: 'grey.200' }}
        />
        {/* Arco de progreso con color dinámico */}
        <CircularProgress
          variant="determinate"
          value={score}
          size={120}
          thickness={4}
          sx={{
            color: getColor(score),
            position: 'absolute',
            left: 0,
          }}
        />
        {/* Número centrado dentro del círculo */}
        <Box sx={{
          position: 'absolute', inset: 0,
          display: 'flex', alignItems: 'center',
          justifyContent: 'center', flexDirection: 'column',
        }}>
          <Typography variant="h4" fontWeight="bold"
            sx={{ color: getColor(score) }}>
            {score.toFixed(0)}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            /100
          </Typography>
        </Box>
      </Box>
      <Typography variant="caption" color="text.secondary">
        Preparación PQC
      </Typography>
    </Box>
  )
}

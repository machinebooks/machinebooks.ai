// Extraído de: LibroCISO/cap-27-executive-dashboard.md
const varColor = d.cyber_risk.cyber_var_95_eur > 5e6
  ? 'text-red-600'      // > 5 millones: rojo
  : d.cyber_risk.cyber_var_95_eur > 1e6
    ? 'text-orange-600'  // 1-5 millones: naranja
    : 'text-green-600'   // < 1 millón: verde

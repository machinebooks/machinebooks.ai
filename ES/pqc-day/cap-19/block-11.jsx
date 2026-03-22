// Extraído de: LibroPQC/cap-19-dashboard.md
<Grid container spacing={3}>
  <Grid item xs={12} sm={6} lg={3}>
    {/* En móvil: 12/12 = fila completa */}
    {/* En tableta: 6/12 = media fila (2 tarjetas por fila) */}
    {/* En escritorio: 3/12 = un cuarto (4 tarjetas por fila) */}
    <KPICard label="Clientes" value={stats.total_clients} />
  </Grid>
</Grid>

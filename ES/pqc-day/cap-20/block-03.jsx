// Extraído de: LibroPQC/cap-20-chat-ia.md
// Colores por estado de la herramienta
const TOOL_STATUS_COLORS = {
  running: 'info',    // azul — en progreso
  success: 'success', // verde — completada
  error:   'error',   // rojo — falló
}

function ToolUseBlock({ tool, isExpanded, onToggle }) {
  const icon = TOOL_ICONS[tool.name] || <CodeIcon fontSize="small" />
  const statusColor = TOOL_STATUS_COLORS[tool.status] || 'default'

  return (
    <Paper variant="outlined" sx={{ mb: 1, overflow: 'hidden' }}>
      {/* Cabecera clicable */}
      <Box onClick={onToggle} sx={{
        display: 'flex', alignItems: 'center', gap: 1,
        px: 1.5, py: 1, cursor: 'pointer',
        bgcolor: 'action.hover',
        '&:hover': { bgcolor: 'action.selected' },
      }}>
        <Box sx={{ color: 'primary.main' }}>{icon}</Box>
        <Typography variant="body2" sx={{ fontWeight: 500, flex: 1 }}>
          {tool.name}
        </Typography>
        {tool.status === 'running' && <CircularProgress size={16} />}
        {tool.status === 'success' && <CheckIcon color="success" />}
        {tool.status === 'error' && <ErrorIcon color="error" />}
      </Box>

      {/* Entrada de la herramienta */}
      {tool.input && (
        <Box sx={{ px: 1.5, py: 0.5, borderTop: 1, borderColor: 'divider' }}>
          <Typography variant="caption" color="text.secondary">
            Input: <code>{JSON.stringify(tool.input).substring(0, 100)}...</code>
          </Typography>
        </Box>
      )}

      {/* Salida colapsable */}
      <Collapse in={isExpanded}>
        <Box component="pre" sx={{
          p: 1, bgcolor: 'grey.900', color: 'grey.100',
          borderRadius: 1, fontSize: '0.75rem',
          overflow: 'auto', maxHeight: 200,
        }}>
          {typeof tool.output === 'string'
            ? tool.output
            : JSON.stringify(tool.output, null, 2)}
        </Box>
      </Collapse>
    </Paper>
  )
}

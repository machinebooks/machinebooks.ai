// Extraído de: LibroPQC/cap-19-dashboard.md
const CategoryCard = ({ title, icon: Icon, color, findings, onClick }) => (
  <Card
    sx={{
      height: '100%',
      cursor: onClick ? 'pointer' : 'default',
      borderLeft: `4px solid ${color}`,
      transition: 'transform 0.2s',
      '&:hover': onClick
        ? { transform: 'translateY(-2px)', boxShadow: 3 }
        : {},
    }}
    onClick={onClick}
  >
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
        <Avatar sx={{ bgcolor: `${color}20`, width: 36, height: 36 }}>
          <Icon sx={{ color, fontSize: 20 }} />
        </Avatar>
        <Typography variant="subtitle1" fontWeight="medium">
          {title}
        </Typography>
      </Box>
      <Typography variant="h4" fontWeight="bold" sx={{ mb: 1 }}>
        {findings.total}
      </Typography>
      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
        {findings.critical > 0 && (
          <Chip size="small" label={`${findings.critical} Críticos`}
            sx={{ bgcolor: '#f4433620', color: '#f44336' }} />
        )}
        {findings.high > 0 && (
          <Chip size="small" label={`${findings.high} Altos`}
            sx={{ bgcolor: '#ff980020', color: '#ff9800' }} />
        )}
      </Box>
    </CardContent>
  </Card>
)

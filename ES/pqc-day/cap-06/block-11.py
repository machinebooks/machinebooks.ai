# Extraído de: LibroPQC/cap-06-seguridad-auditoria.md
# En desarrollo: aceptar cualquier origen
CORS_ORIGINS = '*'

# En producción: restringir a los dominios del frontend
CORS_ORIGINS = 'https://app.ejemplo.com,https://admin.ejemplo.com'

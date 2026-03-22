# Extraído de: LibroUsuario/cap-20-servidores-y-servicios.md
#!/bin/bash
# health-check.sh — Informe de salud del servidor
# Uso: ./health-check.sh > /opt/informes/health_$(date +%Y%m%d).md

echo "# Informe de salud — $(hostname)"
echo "**Fecha:** $(date '+%Y-%m-%d %H:%M')"
echo ""

# 1. Uptime y carga
echo "## Sistema"
echo '
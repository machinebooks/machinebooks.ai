# Extraído de: LibroUsuario/cap-23-tareas-recurrentes.md
#!/bin/bash
# informe-semanal.sh
# Genera el informe semanal de estado del proyecto
# Programado para ejecutarse cada lunes a las 9:00

# Configuración
PROYECTO_DIR="/home/usuario/mi-proyecto"
FECHA=$(date +%Y-%m-%d)
LOG_FILE="$PROYECTO_DIR/scripts/logs/informe-$FECHA.log"

# Crear directorio de logs si no existe
mkdir -p "$PROYECTO_DIR/scripts/logs"

# Registrar inicio
echo "[$FECHA $(date +%H:%M:%S)] Iniciando generación de informe semanal" >> "$LOG_FILE"

# Cambiar al directorio del proyecto (para que Claude Code lea CLAUDE.md)
cd "$PROYECTO_DIR"

# Ejecutar Claude Code en modo no interactivo
claude -p "
Genera el informe semanal de estado del proyecto con fecha $FECHA.

Pasos:
1. Lee datos/tareas.csv y cuenta las tareas por estado
2. Lee datos/incidencias.csv y lista las incidencias abiertas ordenadas por severidad
3. Lee datos/avance.csv y calcula la desviación respecto al plan
4. Genera un informe completo en informes/estado-semanal-$FECHA.md con:
   - Resumen ejecutivo (3 líneas máximo)
   - Tabla de avance: planificado vs. real
   - Tareas completadas esta semana
   - Tareas en curso y pendientes
   - Incidencias abiertas ordenadas por severidad
   - Valoración general y riesgos identificados
5. El informe debe ser claro, profesional y basado únicamente en los datos reales
" >> "$LOG_FILE" 2>&1

# Verificar si se generó el informe
if [ -f "$PROYECTO_DIR/informes/estado-semanal-$FECHA.md" ]; then
    echo "[$FECHA $(date +%H:%M:%S)] Informe generado correctamente" >> "$LOG_FILE"
else
    echo "[$FECHA $(date +%H:%M:%S)] ERROR: No se generó el informe" >> "$LOG_FILE"
fi

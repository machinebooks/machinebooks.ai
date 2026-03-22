# Extraído de: LibroUsuario/cap-23-tareas-recurrentes.md
#!/bin/bash
# Patrón robusto para tareas recurrentes

set -euo pipefail  # Detener ante cualquier error

SCRIPT_NAME="$(basename "$0")"
FECHA=$(date +%Y-%m-%d)
LOG_DIR="/home/usuario/logs"
LOG_FILE="$LOG_DIR/$SCRIPT_NAME-$FECHA.log"
EMAIL_ADMIN="admin@empresa.com"

mkdir -p "$LOG_DIR"

# Función de notificación de error
notificar_error() {
    local mensaje="$1"
    echo "[ERROR] $mensaje" >> "$LOG_FILE"
    claude -p "Envía un email a $EMAIL_ADMIN con asunto 'ERROR en $SCRIPT_NAME ($FECHA)' y cuerpo: $mensaje" 2>/dev/null
}

# Trampa para capturar errores
trap 'notificar_error "El script falló en la línea $LINENO"' ERR

echo "[$(date +%H:%M:%S)] Inicio de $SCRIPT_NAME" >> "$LOG_FILE"

# --- Tu lógica aquí ---

echo "[$(date +%H:%M:%S)] Fin de $SCRIPT_NAME - Completado con éxito" >> "$LOG_FILE"

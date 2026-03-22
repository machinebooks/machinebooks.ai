# Extraído de: LibroUsuario/cap-19-tu-terminal-potenciada.md
#!/bin/bash
# Script de organización de backups
# Generado: 2026-03-21

BACKUP_DIR="/home/backups"
ARCHIVE_DIR="/home/backups/archivo"
LOG_FILE="/home/backups/movimiento.log"
DAYS_OLD=30

# Crear directorio de archivo si no existe
mkdir -p "$ARCHIVE_DIR"

# 1. Ficheros de la última semana
echo "=== Backups de los últimos 7 días ==="
find "$BACKUP_DIR" -maxdepth 1 -type f -mtime -7 \
  -exec ls -lh {} \; | awk '{print $5, $9}'

# 2. Espacio ocupado por backups antiguos (>30 días)
echo ""
echo "=== Espacio ocupado por backups > 30 días ==="
find "$BACKUP_DIR" -maxdepth 1 -type f -mtime +$DAYS_OLD \
  -exec du -ch {} + | tail -1

# 3. Mover ficheros antiguos con registro
echo ""
echo "=== Moviendo ficheros antiguos ==="
echo "--- Movimiento de backups $(date) ---" >> "$LOG_FILE"

find "$BACKUP_DIR" -maxdepth 1 -type f -mtime +$DAYS_OLD | while read f; do
  filename=$(basename "$f")
  echo "Moviendo: $filename" | tee -a "$LOG_FILE"
  mv "$f" "$ARCHIVE_DIR/$filename"
done

echo "Completado. $(wc -l < "$LOG_FILE") entradas en $LOG_FILE"

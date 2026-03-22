# Extraído de: LibroUsuario/cap-23-tareas-recurrentes.md
#!/bin/bash
# backup-diario.sh
# Se ejecuta cada día a las 23:00

FECHA=$(date +%Y-%m-%d)
ORIGEN="/home/usuario/documentos-activos"
DESTINO="/home/usuario/backups"
LOG="/home/usuario/logs/backup-$FECHA.log"

mkdir -p "$DESTINO" /home/usuario/logs

echo "=== Backup diario: $FECHA ===" > "$LOG"

# Paso 1: Crear el backup comprimido
tar -czf "$DESTINO/backup-$FECHA.tar.gz" "$ORIGEN" 2>> "$LOG"

# Paso 2: Verificar que el backup se creó correctamente
if [ -f "$DESTINO/backup-$FECHA.tar.gz" ]; then
    TAMANO=$(du -h "$DESTINO/backup-$FECHA.tar.gz" | cut -f1)
    echo "Backup creado: $TAMANO" >> "$LOG"

    # Paso 3: Usar Claude Code para generar un resumen y verificar
    cd /home/usuario
    claude -p "
    El backup diario se ha completado.
    Archivo: backups/backup-$FECHA.tar.gz
    Tamaño: $TAMANO

    Por favor:
    1. Verifica cuántos archivos hay en documentos-activos/
    2. Lista los 5 archivos modificados más recientemente
    3. Comprueba si hay backups con más de 30 días en backups/ y sugiere cuáles eliminar
    4. Genera un registro breve en logs/backup-resumen-$FECHA.md
    " >> "$LOG" 2>&1

    # Paso 4: Eliminar backups antiguos (más de 30 días)
    find "$DESTINO" -name "backup-*.tar.gz" -mtime +30 -delete

    echo "Backup completado con éxito" >> "$LOG"
else
    echo "ERROR: El backup no se creó" >> "$LOG"

    # Notificar del error
    claude -p "
    ALERTA: El backup diario del $FECHA ha fallado.
    Envía un email a admin@empresa.com con asunto
    'ALERTA: Fallo en backup diario $FECHA'
    explicando que el archivo de backup no se generó correctamente.
    " >> "$LOG" 2>&1
fi

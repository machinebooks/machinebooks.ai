# Extraído de: LibroUsuario/cap-23-tareas-recurrentes.md
# Después de generar el informe...
if [ -f "$PROYECTO_DIR/informes/estado-semanal-$FECHA.md" ]; then
    claude -p "
    Envía por email el informe que se encuentra en
    informes/estado-semanal-$FECHA.md.

    Destinatario: mi.responsable@empresa.com
    Asunto: Informe semanal de estado - Proyecto SGD - $FECHA
    Cuerpo: Adjunto el informe semanal de estado del proyecto.
    Adjunto: el contenido del informe formateado
    " >> "$LOG_FILE" 2>&1
fi

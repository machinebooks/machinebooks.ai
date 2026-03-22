# Extraído de: LibroUsuario/cap-23-tareas-recurrentes.md
#!/bin/bash
# limpieza-semanal.sh
# Se ejecuta cada viernes a las 18:00

FECHA=$(date +%Y-%m-%d)
LOG="/home/usuario/logs/limpieza-$FECHA.log"
mkdir -p /home/usuario/logs

echo "=== Limpieza semanal: $FECHA ===" > "$LOG"

cd /home/usuario

claude -p "
Realiza la limpieza semanal de archivos:

1. En la carpeta Descargas/:
   - Identifica archivos con más de 30 días de antigüedad
   - Lista los archivos que vas a eliminar (NO elimines nada todavía)
   - Mueve esos archivos a una carpeta Descargas/papelera-$FECHA/

2. En la carpeta temporal/:
   - Elimina todos los archivos .tmp y .log con más de 7 días
   - Cuenta cuántos archivos eliminaste y cuánto espacio liberaste

3. En la carpeta proyectos/:
   - Busca archivos duplicados (mismo nombre, diferente ubicación)
   - Genera un informe de duplicados en logs/duplicados-$FECHA.md
   - NO elimines duplicados, solo informa

4. Genera un resumen de la limpieza en logs/limpieza-$FECHA.md con:
   - Archivos movidos a papelera
   - Archivos temporales eliminados
   - Espacio total liberado
   - Duplicados encontrados

IMPORTANTE: No elimines archivos de las carpetas de proyectos activos.
Solo mueve a papelera los de Descargas/ y elimina temporales.
" >> "$LOG" 2>&1

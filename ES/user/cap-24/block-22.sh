# Extraído de: LibroUsuario/cap-24-pipelines-de-datos.md
claude -p "
Revisa los logs de todos los pipelines de la última semana
en la carpeta /home/usuario/logs/.

Para cada pipeline, indica:
- Fecha de última ejecución
- Estado: completado / completado con advertencias / fallido
- Tiempo de ejecución (si está disponible en el log)
- Errores o advertencias encontrados

Genera un resumen en /home/usuario/logs/panel-semanal-$(date +%Y-%m-%d).md
con formato de tabla.
"

# Extraído de: LibroUsuario/cap-25-agentes-en-equipo.md
#!/bin/bash
# preparar-reunion-semanal.sh
# Se ejecuta cada miércoles a las 7:30 (la reunión es a las 10:00)

cd /home/usuario/reunion-seguimiento

# Actualizar datos (si vienen de fuentes externas)
# ... (descarga de datos)

# Lanzar el equipo de agentes
claude -p "
Prepara la reunión de seguimiento del proyecto.
Divide el trabajo en tres tareas paralelas:
[las mismas instrucciones del caso de uso 3]
" > logs/reunion-$(date +%Y-%m-%d).log 2>&1

# Verificar que se generó el dossier
if [ -f "preparacion/dossier-reunion.md" ]; then
    echo "Dossier generado correctamente" >> logs/reunion-$(date +%Y-%m-%d).log
fi

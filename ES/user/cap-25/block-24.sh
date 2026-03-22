# Extraído de: LibroUsuario/cap-25-agentes-en-equipo.md
cd /home/usuario/reunion-seguimiento

claude -p "
Prepara la reunión de seguimiento del proyecto. Divide el trabajo en tres
tareas paralelas:

TAREA 1 — Estado del proyecto:
- Lee datos/tareas-proyecto.csv
- Genera preparacion/estado-proyecto.md con:
  * Porcentaje de avance global
  * Tareas completadas desde la última reunión
  * Tareas en curso con % de progreso
  * Tareas bloqueadas o retrasadas
  * Hitos próximos (próximas 2 semanas)
  * Valoración general: en plazo / con riesgo / retrasado

TAREA 2 — Análisis de incidencias:
- Lee datos/incidencias-abiertas.csv
- Genera preparacion/analisis-incidencias.md con:
  * Tabla de incidencias ordenadas por severidad
  * Para cada incidencia crítica: descripción, impacto y acción propuesta
  * Tendencia: ¿las incidencias están aumentando o disminuyendo?
  * Resumen: cuántas abiertas, cuántas críticas, cuántas llevan más de 7 días

TAREA 3 — Agenda de la reunión:
- Lee datos/acta-reunion-anterior.md y datos/acuerdos-pendientes.csv
- Genera preparacion/agenda-reunion.md con:
  * Revisión de acuerdos pendientes de la reunión anterior
  * Puntos del día priorizados (basados en estado e incidencias)
  * Tiempo estimado por punto (total: máximo 1 hora)
  * Decisiones que se necesitan tomar en esta reunión
  * Participantes sugeridos para cada punto

Cuando las tres tareas terminen, genera un documento único
preparacion/dossier-reunion.md que integre los tres análisis con un
resumen ejecutivo de 5 líneas al principio.
"

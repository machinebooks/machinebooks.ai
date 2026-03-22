# Extraído de: LibroUsuario/cap-25-agentes-en-equipo.md
cd /home/usuario/informe-trimestral

claude -p "
ROLE: Redactor de informes.
Lee los datos en datos/resultados-q1.csv y datos/objetivos-q1.csv.
Genera un informe trimestral completo en borradores/informe-q1-v1.md.

El informe debe tener:
- Resumen ejecutivo (5 líneas)
- Resultados por área (tabla y comentarios)
- Comparativa con objetivos (presupuesto vs. real)
- Análisis de desviaciones (explicar por qué)
- Conclusiones (3-5 puntos accionables)

Requisitos:
- Todas las cifras deben provenir de los CSV, no inventar datos
- Tono profesional, orientado a dirección
- Extensión: 1.500-2.000 palabras
- Formato del glosario.md
" > logs/redactor-v1.log 2>&1

# Extraído de: LibroUsuario/cap-24-pipelines-de-datos.md
claude -p "
PIPELINE DE ANÁLISIS DE SATISFACCIÓN - Q1 2025

FASE 1 - OBTENER:
Lee el archivo datos/encuestas-q1.csv. Verifica que todas las puntuaciones
están entre 1 y 10, que las fechas son del Q1 2025 y que no hay filas
incompletas.

FASE 2 - PREPARAR:
- Calcula la media de cada dimensión (general, comunicación, calidad, plazos)
- Agrupa por cliente para ver tendencias (clientes con múltiples encuestas)
- Agrupa por mes para ver evolución temporal
- Identifica las encuestas con puntuación general < 7 (clientes en riesgo)

FASE 3 - ANALIZAR:
- NPS simplificado: % que recomendarían - % que no recomendarían
- Dimensión mejor valorada y peor valorada
- Evolución mensual: ¿estamos mejorando o empeorando?
- Clientes en riesgo: quiénes puntuaron bajo y en qué dimensiones
- Correlación: ¿los plazos son nuestro punto débil?
- Análisis de comentarios: patrones o temas recurrentes

FASE 4 - ENTREGAR:
Genera informes/satisfaccion-q1-2025.md con:

1. Resumen ejecutivo (5 líneas para dirección)
2. Cuadro de mando: tabla con medias por dimensión y comparativa mensual
3. Ranking de clientes por satisfacción
4. Sección 'Clientes en riesgo' con las encuestas < 7 y plan de acción sugerido
5. Evolución mensual con indicación de tendencia (mejora/empeora/estable)
6. Top 3 áreas de mejora con recomendaciones concretas
7. Citas textuales de los comentarios más relevantes (positivos y negativos)

El tono del informe debe ser profesional, orientado a acciones concretas,
no a estadísticas abstractas. Cada hallazgo debe tener una recomendación asociada.
"

# Extraído de: LibroConsultor/cap-10-estimacion-esfuerzos.md
PLANTILLA_ESTIMACION = """
Necesito estimar el esfuerzo para el siguiente proyecto de consultoría:

## Contexto del proyecto
- **Tipo de servicio**: {tipo_servicio}
- **Sector del cliente**: {sector}
- **Complejidad regulatoria**: {complejidad}
- **Tecnologías en alcance**: {tecnologias}
- **Tamaño del equipo previsto**: {equipo} consultores

## Descripción del alcance
{descripcion_alcance}

## Restricciones conocidas
{restricciones}

## Mi estimación inicial (sin calibrar)
{horas_base} horas, {duracion_semanas} semanas

## Lo que necesito
1. Proyectos históricos similares con su desviación real.
2. Estimación calibrada con intervalo P10-P50-P90.
3. Factores de riesgo específicos de este proyecto.
4. Recomendación sobre dónde añadir buffer.
"""

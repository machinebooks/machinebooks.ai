# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Patrón chain-of-thought para evaluación GO/NO-GO
EVALUATION_PROMPT = """
Analiza el documento de requisitos y determina la viabilidad.

INSTRUCCIONES DE RAZONAMIENTO:
1. Identifica los requisitos técnicos explícitos.
2. Compara cada uno con las capacidades del catálogo de servicios.
3. Identifica gaps: requisitos que no podemos cubrir.
4. Evalúa el riesgo de los gaps identificados.
5. SOLO DESPUÉS de completar los pasos 1-4, emite tu veredicto GO/NO-GO.

FORMATO DE RESPUESTA:
## Razonamiento
[Tu análisis paso a paso]

## Veredicto
GO | NO-GO | CONDICIONAL

## Justificación
[Resumen en 2-3 frases]
"""

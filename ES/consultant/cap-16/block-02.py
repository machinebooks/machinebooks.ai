# Extraído de: LibroConsultor/cap-16-roadmaps-ia.md
def generar_roadmap(assessment: dict, contexto_cliente: dict) -> list[Iniciativa]:
    """Genera roadmap a partir de datos de assessment y contexto."""
    client = anthropic.Anthropic()

    system_prompt = """Eres un consultor senior de IA especializado en
    roadmaps de adopción. Genera iniciativas concretas basadas en:

    REGLAS:
    - Quick wins: máximo 5 iniciativas, todas con ROI demostrable en 90 días
    - Consolidación: 5-8 iniciativas de infraestructura habilitadora
    - Transformación: 3-5 iniciativas estratégicas de alto impacto
    - Cada iniciativa debe tener: nombre, descripción, impacto (1-5),
      esfuerzo (1-5), dependencias, tipo (build/buy/integrate),
      rango presupuestario, equipo necesario, KPI de éxito
    - Las dependencias deben referenciar otras iniciativas por nombre
    - El presupuesto debe ser realista para el sector del cliente
    - Prioriza integrate sobre buy, buy sobre build (salvo diferenciación)

    CATÁLOGO DE PATRONES PROBADOS:
    - Nivel 1→2: chatbot FAQ, automatización documental, dashboards BI con IA
    - Nivel 2→3: pipeline de datos, MLOps básico, gobernanza de IA, RAG interno
    - Nivel 3→4: modelos propios, agentes autónomos, IA embebida en producto
    - Nivel 4→5: IA como ventaja competitiva, ecosistema de agentes, innovación
    """

    mensaje = f"""Assessment del cliente:
    - Sector: {contexto_cliente.get('sector', 'no especificado')}
    - Tamaño: {contexto_cliente.get('empleados', 'N/A')} empleados
    - Presupuesto IT anual: {contexto_cliente.get('presupuesto_it', 'N/A')}
    - Apetito de riesgo: {contexto_cliente.get('apetito_riesgo', 'moderado')}

    Puntuaciones de madurez (1-5):
    - Datos: {assessment.get('datos', 0)}
    - Infraestructura: {assessment.get('infraestructura', 0)}
    - Talento: {assessment.get('talento', 0)}
    - Gobernanza: {assessment.get('gobernanza', 0)}
    - Casos de uso: {assessment.get('casos_uso', 0)}

    Nivel global: {assessment.get('nivel_global', 0)}

    Genera el roadmap completo en formato JSON estructurado."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": mensaje}]
    )

    # Parsear respuesta y construir objetos Iniciativa
    return _parsear_iniciativas(response.content[0].text)

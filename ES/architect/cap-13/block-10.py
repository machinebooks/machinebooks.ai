# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
def clasificar_intent_capa2(consulta: str) -> IntentResult:
    """
    Capa 2: análisis semántico con claude-haiku-4-5.
    Solo se activa cuando la capa 1 no es concluyente.
    Latencia esperada: 100-300ms.
    """
    client = anthropic.Anthropic()  # API key desde variable de entorno

    prompt = f"""Clasifica la siguiente consulta de usuario en una de estas categorías:

- CHAT_RAG: pregunta analítica que requiere buscar en documentos internos (propuestas, CVs, histórico)
- AGENT_TOOLS: búsqueda o filtrado de oportunidades públicas (contratos públicos, concursos, oportunidades)
- WORKFLOW: instrucción para generar o automatizar un documento o proceso
- OFF_TOPIC: consulta fuera del dominio de gestión de oportunidades de negocio

Consulta: "{consulta}"

Responde SOLO con este JSON (sin markdown):
{{"tipo": "TIPO_AQUÍ", "confianza": 0.X, "subtipo": "descripcion_breve", "razonamiento": "una frase"}}"""

    respuesta = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    try:
        datos = json.loads(respuesta.content[0].text.strip())
        return IntentResult(
            tipo=TipoIntent(datos["tipo"]),
            confianza=float(datos["confianza"]),
            subtipo=datos.get("subtipo", ""),
            razonamiento=datos.get("razonamiento", ""),
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        # Fallback seguro si el modelo no devuelve JSON válido
        return IntentResult(
            tipo=TipoIntent.CHAT_RAG,
            confianza=0.5,
            subtipo="fallback",
            razonamiento="Error en clasificación — usando RAG por defecto",
        )


def clasificar_intent(consulta: str) -> IntentResult:
    """
    Punto de entrada principal del clasificador de intención.
    Ejecuta capa 1; si no es concluyente, activa capa 2.
    """
    resultado_capa1 = clasificar_intent_capa1(consulta)
    if resultado_capa1 is not None:
        return resultado_capa1

    # Capa 1 no concluyente → invocar capa 2
    return clasificar_intent_capa2(consulta)

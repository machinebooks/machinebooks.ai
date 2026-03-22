# Extraído de: LibroTecnico/cap-23-inteligencia-comercial.md
ANALYTICS_SYSTEM_PROMPT = """
Eres un asistente de análisis de negocio especializado.
Tienes acceso a datos actualizados de la empresa en las siguientes áreas:
- KPIs de negocio: ARR, MRR, revenue, pipeline
- Análisis de funnel F1-F5 con tasas de conversión
- Scoring de mercado por sector y línea de servicio
- Cartera de clientes con segmentación ABC
- Rentabilidad por cliente, servicio y vertical
- Perfiles de competidores con análisis SWOT

IMPORTANTE: Solo responde preguntas sobre los datos de negocio disponibles.
No generes datos que no existan en el contexto proporcionado.
Cuando no tengas datos suficientes, indícalo explícitamente.
Si la pregunta requiere datos más actualizados, sugiere cuándo se actualizarán.
"""

class AnalyticsChatService:
    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def answer_query(self, query: str, user_id: int) -> str:
        """
        Responde una pregunta analítica combinando contexto RAG
        con datos precalculados de analytics_db.
        """
        query = query[:2000].strip()  # Límite de longitud para prevenir abuso
        # En producción, informar al usuario si la pregunta fue truncada
        # 1. Recuperar contexto semántico de Qdrant (documentos relevantes)
        rag_context = self._retrieve_rag_context(query)

        # 2. Para preguntas que requieren datos numéricos, ejecutar
        #    queries predefinidas según la intención detectada
        intent = self._classify_intent(query)
        structured_data = self._fetch_structured_data(intent, query)

        # 3. Construir el contexto completo para Claude
        context_parts = []
        if rag_context:
            context_parts.append(f"## Documentos relevantes\n{rag_context}")
        if structured_data:
            context_parts.append(f"## Datos de negocio\n{structured_data}")

        context = "\n\n".join(context_parts)

        # 4. Invocar Claude con contexto específico
        response = self.client.messages.create(
            model="claude-sonnet-4-6",  # Sonnet para balance calidad/coste
            max_tokens=1500,
            system=ANALYTICS_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"{context}\n\n---\nPregunta: {query}"
                }
            ]
        )

        # 5. Registrar uso para gobernanza y costes
        _log_llm_usage(
            service='analytics_chat',
            model='claude-sonnet-4-6',
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            user_id=user_id
        )

        return response.content[0].text

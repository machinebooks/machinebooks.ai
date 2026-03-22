# Extraído de: LibroCISO/cap-13-orquestador-copiloto.md
# Ejemplo didáctico: patrones/ai/chat_rag_executor.py

class ChatRAGExecutor:
    """Ejecutor del modo CHAT_RAG: búsqueda semántica + respuesta con fuentes."""

    SYSTEM_PROMPT = """Eres un asistente especializado en regulación y cumplimiento normativo.
Responde SOLO con información basada en los fragmentos normativos proporcionados.
Si la información no está en los fragmentos, di explícitamente que no tienes
información suficiente — nunca inventes artículos, plazos ni requisitos.
Cita siempre la fuente: regulación, artículo y sección cuando sea posible."""

    def __init__(self, rag_service, llm_factory):
        self.rag_service = rag_service
        self.llm_factory = llm_factory

    async def execute(
        self, message: str, module_context: str, session_history: list[dict]
    ) -> AsyncGenerator[dict, None]:
        # 1. Búsqueda semántica en Qdrant
        #    Filtramos por colecciones relevantes según el módulo activo
        collections = self._get_collections_for_module(module_context)
        chunks = await self.rag_service.search(
            query=message,
            collections=collections,
            top_k=6,       # 6 fragmentos es el equilibrio entre contexto y coste
            score_threshold=0.72,  # Umbral mínimo de relevancia semántica
        )

        if not chunks:
            yield {
                "type": "agent_progress",
                "content": "No he encontrado fragmentos normativos relevantes "
                          "para tu consulta. Reformula la pregunta o consulta "
                          "directamente la regulación aplicable.",
            }
            return

        # 2. Construir contexto normativo para el prompt
        context_block = "\n\n---\n\n".join([
            f"**Fuente:** {c.metadata.get('source', 'Desconocida')} "
            f"(relevancia: {c.score:.2f})\n{c.text}"
            for c in chunks
        ])

        # 3. Incluir últimos mensajes de la sesión como contexto conversacional
        #    Limitamos a los 4 últimos intercambios para no saturar la ventana
        recent_history = session_history[-8:]  # 4 pares user/assistant

        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]
        messages.extend(recent_history)
        messages.append({
            "role": "user",
            "content": f"""Contexto normativo relevante:

{context_block}

---

Pregunta del usuario: {message}"""
        })

        # 4. Generar respuesta con streaming
        async for token in self.llm_factory.create_streaming_completion(
            service_name="copilot_chat_rag",
            model_preference="claude-sonnet-4-6",
            messages=messages,
            max_tokens=2048,
        ):
            yield {"type": "agent_progress", "content": token}

    def _get_collections_for_module(self, module_context: str) -> list[str]:
        """Mapea el módulo GRC activo a las colecciones de Qdrant relevantes."""
        mapping = {
            "privacy": ["rgpd", "lopdgdd", "aepd_guides"],
            "risk": ["magerit", "iso27005", "nist_sp800_30", "fair"],
            "compliance": ["ens", "iso27001", "iso27701", "nis2", "dora"],
            "ai_governance": ["ai_act", "iso42001"],
            "general": ["rgpd", "ens", "iso27001", "magerit", "ai_act"],
        }
        return mapping.get(module_context, mapping["general"])

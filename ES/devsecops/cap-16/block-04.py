# Extraído de: LibroDevSecOps/cap-16-data-poisoning-rag.md
class IndirectInjectionDetector:
    """Detecta si una respuesta RAG muestra signos de inyección."""

    DETECTION_PATTERNS = [
        r"(?:como|según)\s+(?:mis|las)\s+instrucciones",
        r"no\s+(?:existen?|hay)\s+requisitos?\s+obligatorios?",
        r"(?:ignora|olvida|descarta)\s+(?:lo|las?|los?)\s+anterior",
        r"(?:en realidad|la verdad es que)\s+no\s+(?:es|son)\s+necesari",
    ]

    def __init__(self, anthropic_client):
        self.claude = anthropic_client

    def check_response(
        self, query: str, context_chunks: list[str],
        response: str
    ) -> dict:
        """Verifica coherencia entre consulta, contexto y respuesta."""
        # Capa 1: patrones estáticos en la respuesta
        static_flags = []
        for pattern in self.DETECTION_PATTERNS:
            if re.search(pattern, response, re.IGNORECASE):
                static_flags.append(pattern[:50])

        # Capa 2: verificación semántica si hay flags
        if static_flags or len(context_chunks) > 3:
            coherence = self._check_semantic_coherence(
                query, context_chunks, response
            )
        else:
            coherence = {"score": 1.0, "concerns": []}

        return {
            "static_flags": static_flags,
            "coherence_score": coherence["score"],
            "concerns": coherence["concerns"],
            "action": (
                "block" if coherence["score"] < 0.3
                else "warn" if coherence["score"] < 0.6
                else "pass"
            ),
        }

    def _check_semantic_coherence(
        self, query: str, chunks: list[str], response: str
    ) -> dict:
        """Usa Claude para verificar coherencia semántica."""
        response_obj = self.claude.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            system=(
                "Analiza si la respuesta es coherente con los chunks "
                "de contexto proporcionados. Detecta si la respuesta "
                "contiene información que NO está en los chunks o que "
                "contradice el conocimiento general del dominio. "
                "Responde en JSON: {\"score\": <0.0-1.0>, "
                "\"concerns\": [\"...\"]}"
            ),
            messages=[{
                "role": "user",
                "content": (
                    f"Consulta: {query}\n\n"
                    f"Chunks de contexto:\n"
                    + "\n---\n".join(chunks[:5])
                    + f"\n\nRespuesta generada:\n{response}"
                )
            }]
        )
        return json.loads(response_obj.content[0].text)

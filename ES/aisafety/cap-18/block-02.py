# Extraido de: LibroAISafety/cap-18-rag-seguridad.md
class ResponseGuard:
    """Protege contra exfiltración de contenido vía respuestas RAG."""

    MAX_CITATION_LENGTH = 200   # caracteres por cita
    MAX_CITATIONS_PER_RESPONSE = 5

    def guard_response(self, response: str,
                       source_documents: list[dict]) -> str:
        """Verifica que la respuesta no exfiltra contenido."""
        # Detectar si la respuesta contiene bloques largos
        # de texto que coinciden con los documentos fuente
        for doc in source_documents:
            doc_text = doc["text"]
            # Buscar coincidencias de más de MAX_CITATION_LENGTH
            overlap = self._find_longest_overlap(response, doc_text)
            if overlap and len(overlap) > self.MAX_CITATION_LENGTH:
                logger.warning(
                    f"Posible exfiltración: respuesta contiene "
                    f"{len(overlap)} chars del documento "
                    f"{doc.get('metadata', {}).get('source', '?')}"
                )
                # Truncar la cita en la respuesta
                response = response.replace(
                    overlap,
                    overlap[:self.MAX_CITATION_LENGTH]
                    + " [... contenido truncado por política "
                    + "de seguridad]"
                )
        return response

    def _find_longest_overlap(self, text_a: str,
                              text_b: str) -> Optional[str]:
        """Encuentra la subcadena común más larga entre dos textos."""
        # Implementación simplificada: busca subcadenas de text_b
        # en text_a con longitud decreciente
        min_len = 50  # mínimo para considerar coincidencia
        for length in range(min(len(text_a), len(text_b)),
                           min_len, -10):
            for start in range(0, len(text_b) - length + 1, 10):
                substring = text_b[start:start + length]
                if substring in text_a:
                    return substring
        return None

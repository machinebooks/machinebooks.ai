# Extracted from: LibroAISafety/ch-18-rag-security.md
class ResponseGuard:
    """Protects against content exfiltration via RAG responses."""

    MAX_CITATION_LENGTH = 200   # characters per citation
    MAX_CITATIONS_PER_RESPONSE = 5

    def guard_response(self, response: str,
                       source_documents: list[dict]) -> str:
        """Verifies that the response does not exfiltrate content."""
        # Detect if the response contains long blocks
        # of text that match source documents
        for doc in source_documents:
            doc_text = doc["text"]
            # Find overlaps longer than MAX_CITATION_LENGTH
            overlap = self._find_longest_overlap(response, doc_text)
            if overlap and len(overlap) > self.MAX_CITATION_LENGTH:
                logger.warning(
                    f"Possible exfiltration: response contains "
                    f"{len(overlap)} chars from document "
                    f"{doc.get('metadata', {}).get('source', '?')}"
                )
                # Truncate the citation in the response
                response = response.replace(
                    overlap,
                    overlap[:self.MAX_CITATION_LENGTH]
                    + " [... content truncated by security "
                    + "policy]"
                )
        return response

    def _find_longest_overlap(self, text_a: str,
                              text_b: str) -> Optional[str]:
        """Finds the longest common substring between two texts."""
        # Simplified implementation: searches for substrings of text_b
        # in text_a with decreasing length
        min_len = 50  # minimum to consider a match
        for length in range(min(len(text_a), len(text_b)),
                           min_len, -10):
            for start in range(0, len(text_b) - length + 1, 10):
                substring = text_b[start:start + length]
                if substring in text_a:
                    return substring
        return None

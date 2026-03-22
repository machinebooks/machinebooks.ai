# Extraído de: LibroPQC/cap-13-rag.md
import tiktoken
import zlib
from typing import List, Dict

class RAGChunker:
    """Fragmentador de documentos con solapamiento controlado"""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoder = tiktoken.get_encoding("cl100k_base")

    def chunk_document(self, content: bytes, title: str) -> List[Dict]:
        """
        Fragmentar documento comprimido en chunks con metadatos.
        Respeta límites de sección cuando es posible.
        """
        # Descomprimir contenido
        text = zlib.decompress(content).decode('utf-8')
        tokens = self.encoder.encode(text)
        total_tokens = len(tokens)

        chunks = []
        start = 0
        chunk_index = 0

        while start < total_tokens:
            end = min(start + self.chunk_size, total_tokens)
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoder.decode(chunk_tokens)

            # Intentar cortar en un límite de párrafo
            if end < total_tokens:
                chunk_text = self._adjust_boundary(chunk_text)

            chunks.append({
                'index': chunk_index,
                'text': chunk_text,
                'token_count': len(self.encoder.encode(chunk_text)),
                'source_title': title,
                'start_token': start,
                'end_token': end,
            })

            # Avanzar con solapamiento
            start = end - self.chunk_overlap
            chunk_index += 1

        return chunks

    def _adjust_boundary(self, text: str) -> str:
        """Ajustar el corte al último párrafo completo"""
        last_para = text.rfind('\n\n')
        if last_para > len(text) * 0.7:  # No cortar más del 30%
            return text[:last_para]
        last_sentence = text.rfind('. ')
        if last_sentence > len(text) * 0.8:
            return text[:last_sentence + 1]
        return text

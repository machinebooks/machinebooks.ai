# Extraido de: LibroAISafety/cap-18-rag-seguridad.md
import hashlib
from typing import Optional

class DocumentWatermarker:
    """Inserta marcadores únicos en documentos antes de indexar."""

    # Caracteres Unicode de anchura cero usados como marcadores
    ZERO_WIDTH_CHARS = [
        "\u200b",  # Zero-width space
        "\u200c",  # Zero-width non-joiner
        "\u200d",  # Zero-width joiner
        "\ufeff",  # Zero-width no-break space
    ]

    def watermark(self, text: str, doc_id: str,
                  tenant_id: str) -> str:
        """Inserta un watermark basado en doc_id y tenant_id."""
        # Generar secuencia de bits del watermark
        wm_input = f"{doc_id}:{tenant_id}"
        wm_hash = hashlib.sha256(wm_input.encode()).hexdigest()
        # Convertir los primeros 16 hex chars a bits
        bits = bin(int(wm_hash[:16], 16))[2:].zfill(64)
        # Insertar caracteres de anchura cero cada N palabras
        words = text.split()
        watermarked = []
        bit_idx = 0
        for i, word in enumerate(words):
            watermarked.append(word)
            if i % 10 == 9 and bit_idx < len(bits):
                # Insertar carácter según el bit
                char_idx = int(bits[bit_idx:bit_idx+2], 2) % 4
                watermarked.append(self.ZERO_WIDTH_CHARS[char_idx])
                bit_idx += 2
        return " ".join(watermarked)

    def extract_watermark(self, text: str) -> Optional[str]:
        """Extrae el watermark de un texto marcado."""
        bits = []
        for char in text:
            if char in self.ZERO_WIDTH_CHARS:
                idx = self.ZERO_WIDTH_CHARS.index(char)
                bits.append(format(idx, '02b'))
        if len(bits) < 8:
            return None
        return "".join(bits)

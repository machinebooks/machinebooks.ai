# Extracted from: LibroAISafety/ch-18-rag-security.md
import hashlib
from typing import Optional

class DocumentWatermarker:
    """Inserts unique markers in documents before indexing."""

    # Zero-width Unicode characters used as markers
    ZERO_WIDTH_CHARS = [
        "\u200b",  # Zero-width space
        "\u200c",  # Zero-width non-joiner
        "\u200d",  # Zero-width joiner
        "\ufeff",  # Zero-width no-break space
    ]

    def watermark(self, text: str, doc_id: str,
                  tenant_id: str) -> str:
        """Inserts a watermark based on doc_id and tenant_id."""
        # Generate watermark bit sequence
        wm_input = f"{doc_id}:{tenant_id}"
        wm_hash = hashlib.sha256(wm_input.encode()).hexdigest()
        # Convert first 16 hex chars to bits
        bits = bin(int(wm_hash[:16], 16))[2:].zfill(64)
        # Insert zero-width characters every N words
        words = text.split()
        watermarked = []
        bit_idx = 0
        for i, word in enumerate(words):
            watermarked.append(word)
            if i % 10 == 9 and bit_idx < len(bits):
                # Insert character based on bit
                char_idx = int(bits[bit_idx:bit_idx+2], 2) % 4
                watermarked.append(self.ZERO_WIDTH_CHARS[char_idx])
                bit_idx += 2
        return " ".join(watermarked)

    def extract_watermark(self, text: str) -> Optional[str]:
        """Extracts the watermark from a marked text."""
        bits = []
        for char in text:
            if char in self.ZERO_WIDTH_CHARS:
                idx = self.ZERO_WIDTH_CHARS.index(char)
                bits.append(format(idx, '02b'))
        if len(bits) < 8:
            return None
        return "".join(bits)

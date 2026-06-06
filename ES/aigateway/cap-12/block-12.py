# Extraído de: LibroAIGateway/cap-12-cola-rag.md
# gateway/app/services/rag_service.py:1257-1304 (sintetizado)
@staticmethod
def _split_text(text, chunk_size=1500, chunk_overlap=200):
    """Divide por párrafos primero, luego por oraciones."""
    paragraphs = text.split("\n\n")
    chunks, current_chunk = [], ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current_chunk) + len(para) + 2 <= chunk_size:
            # Cabe: añadir al chunk actual
            current_chunk = (current_chunk + "\n\n" + para if current_chunk else para)
        else:
            # Llenar chunk actual y empezar uno nuevo
            if current_chunk:
                chunks.append(current_chunk)
            if len(para) > chunk_size:
                # Párrafo muy largo: dividir por oraciones
                sentences = para.replace(". ", ".\n").split("\n")
                # ... acumular oraciones hasta chunk_size ...
            else:
                current_chunk = para

    # Overlap: cola del chunk anterior + chunk siguiente
    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i - 1][-chunk_overlap:]
            overlapped.append(prev_tail + "\n" + chunks[i])
        chunks = overlapped
    return chunks

# Extraído de: LibroConsultor/cap-04-rag-conocimiento.md
def chunk_document(text: str, metadata: DocumentMetadata) -> list[dict]:
    """Fragmenta un documento respetando estructura y aplicando ventana."""
    sections = split_by_headers(text)  # divide por # y ##
    chunks = []

    for section_title, section_text in sections:
        tokens = tokenize(section_text)

        if len(tokens) <= CHUNK_SIZE:
            # Sección corta: un solo fragmento
            chunks.append({
                "text": f"{section_title}\n\n{section_text}",
                "section": section_title,
                "metadata": metadata.__dict__,
                "doc_hash": hashlib.md5(section_text.encode()).hexdigest()
            })
        else:
            # Sección larga: ventana deslizante
            for i in range(0, len(tokens), CHUNK_SIZE - CHUNK_OVERLAP):
                window = tokens[i:i + CHUNK_SIZE]
                chunk_text = detokenize(window)
                chunks.append({
                    "text": f"{section_title}\n\n{chunk_text}",
                    "section": section_title,
                    "metadata": metadata.__dict__,
                    "doc_hash": hashlib.md5(
                        chunk_text.encode()
                    ).hexdigest()
                })
    return chunks

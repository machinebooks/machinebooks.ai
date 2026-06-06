# Extraído de: LibroAIGateway/cap-10-embeddings-imagenes-audio.md
# gateway/app/api/v1/embeddings.py:85-89
if model_row.capability != "embedding":
    raise HTTPException(
        400,
        f"El modelo '{body.model}' es de tipo {model_row.capability}, no embedding.",
    )

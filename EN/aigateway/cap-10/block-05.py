# Extracted from: LibroAIGateway/cap-10-embeddings-images-audio.md
# gateway/app/api/v1/embeddings.py:85-89
if model_row.capability != "embedding":
    raise HTTPException(
        400,
        f"The model '{body.model}' is of type {model_row.capability}, not embedding.",
    )

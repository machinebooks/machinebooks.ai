# Extraído de: LibroAIGateway/cap-10-embeddings-imagenes-audio.md
# gateway/app/api/v1/audio.py:248-253 (sintetizado)
async with httpx.AsyncClient(timeout=60.0) as client:
    azure_resp = await client.post(
        url, json=payload,
        headers={"api-key": api_key, "Content-Type": "application/json"},
    )
    azure_resp.raise_for_status()

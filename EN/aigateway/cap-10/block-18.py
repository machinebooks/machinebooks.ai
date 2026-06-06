# Extracted from: LibroAIGateway/cap-10-embeddings-images-audio.md
# gateway/app/api/v1/audio.py:248-253 (synthesized)
async with httpx.AsyncClient(timeout=60.0) as client:
    azure_resp = await client.post(
        url, json=payload,
        headers={"api-key": api_key, "Content-Type": "application/json"},
    )
    azure_resp.raise_for_status()

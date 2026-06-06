# Extraído de: LibroAIGateway/cap-10-embeddings-imagenes-audio.md
# gateway/app/api/v1/audio.py:268-271 (sintetizado)
tts_input_tok = max(1, len(sanitized_input))
tts_cost = await CostService.calculate(
    model_key, tts_input_tok, 0, db, organization_id=org_id,
) or 0.0

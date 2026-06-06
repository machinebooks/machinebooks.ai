# Extraído de: LibroAIGateway/cap-10-embeddings-imagenes-audio.md
# gateway/app/api/v1/images.py:236-246 (sintetizado)
usage = (response or {}).get("usage")
img_prompt_tok = int((usage or {}).get("input_tokens") or 0)
img_output_tok = int((usage or {}).get("output_tokens") or 0)
if img_prompt_tok == 0 and img_output_tok == 0:
    # Fallback: ~1 token cada 4 chars del prompt + flat por imagen
    img_prompt_tok = max(1, len(sanitized_prompt) // 4)
    img_output_tok = 1
cost = await CostService.calculate(
    deployment_key, img_prompt_tok, img_output_tok, db, organization_id=org_id,
) or 0.0

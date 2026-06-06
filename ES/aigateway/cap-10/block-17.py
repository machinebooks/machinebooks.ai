# Extraído de: LibroAIGateway/cap-10-embeddings-imagenes-audio.md
# gateway/app/api/v1/audio.py:220-224 (sintetizado)
PolicyService.check_injection(body.input)
sanitized_input = PolicyService.sanitize_input_variables(body.input)
sanitized_input, pii_count, pii_types = await PolicyService.scan_and_sanitize(
    sanitized_input, db, organization_id=org_id,
)

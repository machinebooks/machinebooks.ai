# Extraído de: LibroAIGateway/cap-10-embeddings-imagenes-audio.md
# gateway/app/api/v1/embeddings.py:62-75 (sintetizado)
sanitized_inputs: List[str] = []
pii_total = 0
pii_types_set: set[str] = set()

for raw in inputs:
    PolicyService.check_injection(raw)            # 1. anti-injection
    clean = PolicyService.sanitize_input_variables(raw)  # 2. sanitizar vars
    clean, pii_count, pii_types = await PolicyService.scan_and_sanitize(
        clean, db, organization_id=org_id,         # 3. PII por org
    )
    sanitized_inputs.append(clean)
    pii_total += pii_count
    if pii_types:
        pii_types_set.update(pii_types)

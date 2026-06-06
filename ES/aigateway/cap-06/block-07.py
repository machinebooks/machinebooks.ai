# Extraído de: LibroAIGateway/cap-06-deployment-fallback.md
if estimated_tokens > 0 and redis is not None:
    for d in rows:
        if not d.tpm_quota:
            ok_rows.append(d)
            continue
        avail = await cls._available_tpm(redis, d)
        if avail >= estimated_tokens:
            ok_rows.append(d)

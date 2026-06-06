# Extraído de: LibroAIGateway/cap-11-tools-codigo-web-documentos.md
async def _safe_get_with_redirects(client, url):
    current = url
    for _hop in range(_MAX_FETCH_REDIRECTS + 1):
        parsed = urlparse(current)
        if parsed.scheme not in ("http", "https"):
            raise HTTPException(400, "Redirect a esquema no permitido")
        if _is_private_host(parsed.hostname or ""):
            raise HTTPException(400, "URL apunta a red privada/loopback")
        resp = await client.get(current)
        if resp.status_code in (301, 302, 303, 307, 308):
            loc = resp.headers.get("location") or ""
            current = urljoin(current, loc)  # resuelve relative redirects
            continue
        return resp
    raise HTTPException(502, "Demasiados redirects")

# Extraído de: LibroAIGateway/cap-11-tools-codigo-web-documentos.md
# Selección de provider de búsqueda
if brave_key:
    results = await _search_brave(body.query, body.count, brave_key)
elif serper_key:
    results = await _search_serper(body.query, body.count, serper_key)
else:
    results = await _search_ddg(body.query, body.count)

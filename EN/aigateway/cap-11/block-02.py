# Extracted from: LibroAIGateway/cap-11-tools-code-web-documents.md
# Search provider selection
if brave_key:
    results = await _search_brave(body.query, body.count, brave_key)
elif serper_key:
    results = await _search_serper(body.query, body.count, serper_key)
else:
    results = await _search_ddg(body.query, body.count)

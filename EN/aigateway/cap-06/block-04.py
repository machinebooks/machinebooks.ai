# Extracted from: LibroAIGateway/cap-06-deployment-fallback.md
if required_tags:
    tag_set = set(required_tags)
    rows = [d for d in rows if tag_set.issubset(set(d.tags or []))]

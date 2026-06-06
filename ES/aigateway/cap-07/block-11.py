# Extraído de: LibroAIGateway/cap-07-adapters.md
# Busca tool_use_ids que SÍ tienen tool_result
matched_ids = {b["tool_use_id"] for msg in conversation
               for b in (msg.get("content") or [])
               if isinstance(b, dict) and b.get("type") == "tool_result"}
# Elimina tool_use huérfanos
filtered = [b for b in content
            if not (b.get("type") == "tool_use" and b.get("id") not in matched_ids)]

# Extracted from: LibroAIGateway/cap-07-adapters.md
# Find tool_use_ids that DO have tool_result
matched_ids = {b["tool_use_id"] for msg in conversation
               for b in (msg.get("content") or [])
               if isinstance(b, dict) and b.get("type") == "tool_result"}
# Remove orphan tool_use
filtered = [b for b in content
            if not (b.get("type") == "tool_use" and b.get("id") not in matched_ids)]

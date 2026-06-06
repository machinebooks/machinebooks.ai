# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/output_filter_service.py:268-273

combined = accumulated + chunk
# We only scan the tail of the buffer: regex over the entire response on
# every chunk would be O(n^2). 1.5KB is enough to capture long tokens
# like JWTs (>500 chars) and full PEM headers.
tail = combined[-1500:]

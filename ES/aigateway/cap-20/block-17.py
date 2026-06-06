# Extraído de: LibroAIGateway/cap-20-clasificacion-guardrails-firewall.md
# gateway/app/services/output_filter_service.py:268-273

combined = accumulated + chunk
# Solo escaneamos la cola del buffer: regex sobre toda la respuesta en
# cada chunk sería O(n^2). 1.5KB es suficiente para capturar tokens
# largos como JWTs (>500 chars) y headers PEM completos.
tail = combined[-1500:]

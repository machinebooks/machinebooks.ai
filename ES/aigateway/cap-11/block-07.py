# Extraído de: LibroAIGateway/cap-11-tools-codigo-web-documentos.md
# HTML → texto plano en el fetch
text = re.sub(r"<script[\s\S]*?</script>", "", text, flags=re.IGNORECASE)
text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.IGNORECASE)
text = re.sub(r"</(p|div|h[1-6]|li|tr|br|hr)[^>]*>", "\n", text, flags=re.IGNORECASE)
text = re.sub(r"<(br|hr)\s*/?>", "\n", text, flags=re.IGNORECASE)
text = _strip_tags(text)          # elimina todas las etiquetas restantes
text = re.sub(r"\n{3,}", "\n\n", text)  # colapsa líneas en blanco

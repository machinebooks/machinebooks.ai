# Extraído de: LibroTecnico/cap-24-documentacion-ia.md
# Fase 1: generación
borrador = generar_documentacion(contexto, prompt_generacion)

# Fase 2: revisión con Claude (diferente instancia)
revision_prompt = f"""Revisa este borrador de documentación técnica:

{borrador}

Verifica:
1. ¿Hay afirmaciones técnicas que podrían ser incorrectas o ambiguas?
2. ¿Hay pasos de las guías que un usuario podría ejecutar de forma incorrecta?
3. ¿Hay información que parece sensible y no debería estar en documentación pública?
4. ¿Qué secciones están incompletas o poco desarrolladas?

Proporciona una lista de observaciones concretas, no el texto corregido."""

observaciones = client.messages.create(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": revision_prompt}]
)

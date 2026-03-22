# Extraído de: LibroTecnico/cap-15-interfaces-chat.md
def build_system_prompt(
    base_context: dict,
    memories: list[UserMemory]
) -> str:
    """
    Construye el system prompt enriquecido con memorias del usuario.
    Las memorias se agrupan por categoría para facilitar la lectura del modelo.
    """
    base_prompt = get_base_prompt(base_context.get("chat_type", "general"))

    if not memories:
        return base_prompt

    # Agrupar por categoría
    by_category: dict[str, list[str]] = {}
    for memory in memories:
        cat = memory.category.value
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(memory.content)

    # Construir bloque de contexto del usuario
    memory_block = "\n\n## Contexto del usuario\n"
    category_labels = {
        "preferences": "Preferencias de trabajo",
        "client_facts": "Información sobre clientes",
        "workflow_patterns": "Patrones de trabajo habituales",
        "insights": "Conclusiones y aprendizajes previos"
    }

    for category, items in by_category.items():
        label = category_labels.get(category, category)
        memory_block += f"\n### {label}\n"
        for item in items:
            memory_block += f"- {item}\n"

    memory_block += "\nUsa este contexto para personalizar tus respuestas. "
    memory_block += "No menciones explícitamente que tienes estas memorias a menos que sea relevante."

    return base_prompt + memory_block

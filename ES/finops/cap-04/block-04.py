# Extraído de: LibroFinOps/cap-04-instrumentacion-llm.md
# El código de negocio no cambia
llm = LLMUsageTracker(
    base_llm=ChatAnthropic(model="claude-sonnet-4-6"),
    service_name="document_analysis",
    user_id=current_user.id
)

# La llamada es idéntica
response = await llm.ainvoke(messages)

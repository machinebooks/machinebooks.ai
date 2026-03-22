# Extraído de: LibroFinOps/cap-06-atribucion.md
# En el middleware de autenticación multi-tenant
llm = LLMUsageTracker(
    base_llm=ChatAnthropic(model="claude-sonnet-4-6"),
    service_name="document_analysis",
    calling_app="document_analyzer",
    user_id=current_user.id,
    tenant_id=current_user.tenant_id,   # dimensión adicional para SaaS
)

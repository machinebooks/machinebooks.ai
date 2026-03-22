# Extraído de: LibroFinOps/cap-04-instrumentacion-llm.md
# Uso del callback en un agente de análisis
handler = CostTrackingCallbackHandler(
    service_name="document_analysis_agent",
    user_id=current_user.id,
)
result = await agent.ainvoke(
    {"input": document_text},
    config={"callbacks": [handler]},
)

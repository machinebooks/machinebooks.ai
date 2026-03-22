# Source: The FinOps Engineer and the Machine -- Chapter 4
# Pattern: LLMUsageTracker -- decorator pattern for cost tracking

# Business code does not change
llm = LLMUsageTracker(
    base_llm=ChatAnthropic(model="claude-sonnet-4-6"),
    service_name="document_analysis",
    user_id=current_user.id
)

# The call is identical
response = await llm.ainvoke(messages)

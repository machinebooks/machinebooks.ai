# Source: The FinOps Engineer and the Machine -- Chapter 21
# Pattern: LLM audit model with AI Act compliance fields

# models/llm_audit.py (continued)
class LLMInteractionContent(Base):
    """
    Prompt and response content. Retention: 90 days.
    Automatically deleted unless marked as
    decision_relevant in the associated LLMUsageLog.
    """
    __tablename__ = "llm_interaction_content"

    id = Column(Integer, primary_key=True)
    usage_log_id = Column(Integer, ForeignKey("llm_usage_log.id"), unique=True)
    prompt_text = Column(Text)
    response_text = Column(Text)
    system_prompt_hash = Column(String(64))  # hash of the system prompt
    expires_at = Column(DateTime, nullable=False)

    usage_log = relationship("LLMUsageLog", backref="interaction_content")

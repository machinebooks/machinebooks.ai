# Extracted from: LibroAIGateway/cap-12-queue-rag.md
# gateway/app/api/v1/llm_queued.py:69-84
class QueuedLLMRequest(BaseModel):
    system_prompt: str = Field(
        "", max_length=500_000,  # ~125k tokens
        description="System instructions",
    )
    user_prompt: str = Field(
        ..., min_length=1, max_length=500_000,
        description="User message",
    )
    purpose: Literal["wizard", "wizard_full",
                     "default", "code"] = Field(
        "wizard", description="Defines model + config",
    )
    reasoning_effort: Optional[
        Literal["none","minimal","low","medium","high","xhigh"]
    ] = None
    extra_params: Optional[dict[str, Any]] = None

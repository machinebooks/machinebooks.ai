# Extraído de: LibroAIGateway/cap-12-cola-rag.md
# gateway/app/api/v1/llm_queued.py:69-84
class QueuedLLMRequest(BaseModel):
    system_prompt: str = Field(
        "", max_length=500_000,  # ~125k tokens
        description="Instrucciones de sistema",
    )
    user_prompt: str = Field(
        ..., min_length=1, max_length=500_000,
        description="Mensaje user",
    )
    purpose: Literal["wizard", "wizard_full",
                     "default", "code"] = Field(
        "wizard", description="Define modelo + config",
    )
    reasoning_effort: Optional[
        Literal["none","minimal","low","medium","high","xhigh"]
    ] = None
    extra_params: Optional[dict[str, Any]] = None

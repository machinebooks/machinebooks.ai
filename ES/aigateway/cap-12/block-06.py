# Extraído de: LibroAIGateway/cap-12-cola-rag.md
# gateway/app/api/v1/llm_queued.py:199-225 (sintetizado)
n7x_job_id = request.headers.get("X-N7x-Job-Id")[:36] or None
n7x_workspace_id = request.headers.get("X-N7x-Workspace-Id")[:100] or None
n7x_conversation_id = request.headers.get("X-N7x-Conversation-Id")[:36] or None

async_result = call_llm.apply_async(
    kwargs={
        "system_prompt": body.system_prompt,
        "user_prompt": body.user_prompt,
        "purpose": body.purpose,
        "organization_id": org_id,
        "user_id": user_id,
        "reasoning_effort": body.reasoning_effort,
        "extra_params": body.extra_params,
        "device_id": device_id,
        "job_id": n7x_job_id,
        "workspace_id": n7x_workspace_id,
        "conversation_id": n7x_conversation_id,
    },
    queue="llm",
    priority=priority,
)

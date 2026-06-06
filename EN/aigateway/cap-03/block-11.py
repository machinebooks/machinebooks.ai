# Extracted from: LibroAIGateway/cap-03-pipeline-stages.md
# audit: response headers for real-time observability
headers = {
    "X-N7x-Model-Used": model_used,
    "X-N7x-Multiplier": str(ctx.multiplier),
    "X-N7x-Auto-Routed": "true" if ctx.was_auto_routed else "false",
    "X-N7x-Cost-Eur": f"{float(cost_usd):.6f}",
    "X-N7x-Latency-Ms": str(int(latency_ms)),
    "X-N7x-Prompt-Tokens": str(prompt_tokens),
    "X-N7x-Cache-Hit-Pct": f"{ratio:.1f}",  # only if cached_tokens > 0
}

# Extraído de: LibroAIGateway/cap-03-pipeline-stages.md
# audit: headers de respuesta para observabilidad en tiempo real
headers = {
    "X-N7x-Model-Used": model_used,
    "X-N7x-Multiplier": str(ctx.multiplier),
    "X-N7x-Auto-Routed": "true" if ctx.was_auto_routed else "false",
    "X-N7x-Cost-Eur": f"{float(cost_usd):.6f}",
    "X-N7x-Latency-Ms": str(int(latency_ms)),
    "X-N7x-Prompt-Tokens": str(prompt_tokens),
    "X-N7x-Cache-Hit-Pct": f"{ratio:.1f}",  # solo si cached_tokens > 0
}

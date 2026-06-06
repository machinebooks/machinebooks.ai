# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/guardrail_service.py:191-199

try:
    # Audit A1: hard timeout against ReDoS.
    match = pattern.search(out, timeout=timeout_s)
except TimeoutError:
    logger.warning(
        "guardrail:redos_timeout name=%s category=%s timeout_s=%s",
        g.name, g.category, timeout_s,
    )
    continue

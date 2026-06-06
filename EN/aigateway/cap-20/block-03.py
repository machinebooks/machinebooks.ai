# Extracted from: LibroAIGateway/cap-20-classification-guardrails-firewall.md
# gateway/app/services/content_classifier_service.py:147-170

# Calculate risk score
severity_scores = {"critical": 40, "high": 25, "medium": 15, "low": 5}
result.risk_score += severity_scores.get(severity, 10)

# If the action is block, mark for blocking
if action == "block":
    result.blocked = True
    result.block_reason = (
        f"Content blocked: detected {cat.get('name', slug)} "
        f"(severity: {severity})"
    )

# Raise exception if blocked
if result.blocked:
    raise PolicyBlocked(result.block_reason)

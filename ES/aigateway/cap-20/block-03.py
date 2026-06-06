# Extraído de: LibroAIGateway/cap-20-clasificacion-guardrails-firewall.md
# gateway/app/services/content_classifier_service.py:147-170

# Calcular risk score
severity_scores = {"critical": 40, "high": 25, "medium": 15, "low": 5}
result.risk_score += severity_scores.get(severity, 10)

# Si la acción es block, marcar para bloqueo
if action == "block":
    result.blocked = True
    result.block_reason = (
        f"Contenido bloqueado: detectado {cat.get('name', slug)} "
        f"(severidad: {severity})"
    )

# Lanzar excepción si hay bloqueo
if result.blocked:
    raise PolicyBlocked(result.block_reason)

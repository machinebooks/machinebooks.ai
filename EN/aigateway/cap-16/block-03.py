# Extracted from: LibroAIGateway/cap-16-jwt-device-binding.md
# Hardcoded whitelist — "none" is never accepted (gateway/app/core/security.py)
ALLOWED_JWT_ALGORITHMS = ("HS256", "HS384", "HS512")

def _ensure_jwt_algorithm_safe() -> None:
    alg = getattr(settings, "JWT_ALGORITHM", None)
    if alg not in ALLOWED_JWT_ALGORITHMS:
        raise RuntimeError(
            f"JWT_ALGORITHM inválido: {alg!r}. "
            f"Permitidos: {ALLOWED_JWT_ALGORITHMS}"
        )

_ensure_jwt_algorithm_safe()  # Executes at import-time

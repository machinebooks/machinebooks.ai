# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico: patrones/ai_service/circuit_breaker.py
class ProviderCircuitBreaker:
    """
    Circuit breaker por proveedor.
    Estados: CLOSED (normal) → OPEN (fallo) → HALF_OPEN (test)
    """

    FAILURE_THRESHOLD = 5       # Fallos para abrir el circuito
    RECOVERY_TIMEOUT_S = 120    # Segundos antes de intentar recuperar
    SUCCESS_THRESHOLD = 2       # Éxitos en HALF_OPEN para cerrar

    def record_success(self, provider: str):
        state = self._get_state(provider)
        if state == "half_open":
            # Incrementar contador de éxitos en recuperación
            successes = self._redis.incr(f"cb:{provider}:successes")
            if successes >= self.SUCCESS_THRESHOLD:
                self._set_state(provider, "closed")
                self._redis.delete(f"cb:{provider}:failures")

    def record_failure(self, provider: str):
        failures = self._redis.incr(f"cb:{provider}:failures")
        self._redis.expire(f"cb:{provider}:failures", 30)

        if failures >= self.FAILURE_THRESHOLD:
            self._set_state(provider, "open")
            self._redis.setex(
                f"cb:{provider}:open_until",
                self.RECOVERY_TIMEOUT_S,
                "1"
            )

    def is_available(self, provider: str) -> bool:
        state = self._get_state(provider)
        if state == "closed":
            return True
        if state == "open":
            # Verificar si ha pasado el timeout de recuperación
            if not self._redis.exists(f"cb:{provider}:open_until"):
                self._set_state(provider, "half_open")
                return True  # Permitir una petición de prueba
            return False
        # half_open: permitir peticiones de prueba
        return True

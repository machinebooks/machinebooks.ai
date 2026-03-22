# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico: patrones/ai_service/rate_limiter.py
class LLMRateLimiter:
    """
    Rate limiting preventivo por proveedor.
    Opera en ventana deslizante de 60 segundos.
    """

    # Límites conservadores (80% del límite real del proveedor)
    PROVIDER_LIMITS = {
        "anthropic": {"rpm": 400, "tpm": 80_000},
        "azure_openai": {"rpm": 240, "tpm": 150_000},
        "ollama": {"rpm": 60, "tpm": None},  # Sin límite de tokens en local
    }

    def check_and_consume(self, provider: str, estimated_tokens: int) -> bool:
        """
        Verifica si la petición puede procesarse sin superar límites.
        Retorna False si hay que throttle.
        """
        rpm_key = f"rate:{provider}:rpm:{self._current_minute()}"
        tpm_key = f"rate:{provider}:tpm:{self._current_minute()}"

        limits = self.PROVIDER_LIMITS.get(provider, {})

        # Verificar RPM
        current_rpm = int(self._redis.get(rpm_key) or 0)
        if limits.get("rpm") and current_rpm >= limits["rpm"]:
            return False  # Rate limit alcanzado

        # Verificar TPM si aplica
        if limits.get("tpm"):
            current_tpm = int(self._redis.get(tpm_key) or 0)
            if current_tpm + estimated_tokens > limits["tpm"]:
                return False  # Token limit alcanzado

        # Consumir capacidad
        self._redis.incr(rpm_key)
        self._redis.expire(rpm_key, 60)
        if estimated_tokens and limits.get("tpm"):
            self._redis.incrby(tpm_key, estimated_tokens)
            self._redis.expire(tpm_key, 60)

        return True

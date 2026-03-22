# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# Detector de fuerza bruta integrado en el middleware
class SecurityEventDetector:
    """Detector en memoria de patrones sospechosos."""

    def __init__(self):
        self.failed_login_cache: dict[str, list[datetime]] = {}

    async def analyze_login_attempt(self, ip_address: str, success: bool):
        if success or not ip_address:
            return

        now = datetime.utcnow()
        threshold_minutes = 15
        max_attempts = 5

        # Limpiar cache de intentos antiguos
        if ip_address in self.failed_login_cache:
            self.failed_login_cache[ip_address] = [
                ts for ts in self.failed_login_cache[ip_address]
                if (now - ts).total_seconds() < threshold_minutes * 60
            ]
        else:
            self.failed_login_cache[ip_address] = []

        self.failed_login_cache[ip_address].append(now)

        if len(self.failed_login_cache[ip_address]) >= max_attempts:
            logger.warning(
                f"Brute force detected: {len(self.failed_login_cache[ip_address])} "
                f"failed attempts from {ip_address}"
            )

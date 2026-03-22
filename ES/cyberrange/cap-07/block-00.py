# Extraído de: LibroCyberrange/cap-07-redes-aislamiento.md
# Ejemplo didáctico: services/pfsense_service.py — Cliente pfSense

class PfSenseClient:
    """Cliente para una instancia pfSense (una por workzone)."""

    def __init__(self, host: str, api_key: str, port: int = 443):
        self.host = host
        self.port = port
        self.base_url = f"https://{host}:{port}/api/v2"
        self.api_key = api_key
        self.timeout = (10, 30)  # (connect, read) en segundos
        self.verify_ssl = False  # Certificados autofirmados en lab

    def _headers(self) -> dict:
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _request(self, method: str, endpoint: str,
                 data: dict = None) -> dict:
        """Ejecutar petición HTTP contra la API de pfSense."""
        url = f"{self.base_url}{endpoint}"
        try:
            resp = requests.request(
                method, url,
                headers=self._headers(),
                json=data,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            resp.raise_for_status()
            return resp.json() if resp.text else {}
        except requests.exceptions.ConnectionError:
            logger.error(
                f"No se puede conectar a pfSense en {self.host}:{self.port}"
            )
            raise
        except requests.exceptions.HTTPError as e:
            logger.error(
                f"Error API pfSense: {e.response.status_code} "
                f"- {e.response.text}"
            )
            raise

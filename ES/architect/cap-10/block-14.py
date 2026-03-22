# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
# Ejemplo didáctico: patrones/automation/onedrive_sync.py

import httpx
from datetime import datetime, timedelta

class OneDriveSyncBot:
    """Sincronizador de documentos desde OneDrive/SharePoint.

    No usa Selenium — accede directamente a la API de Microsoft Graph
    con autenticación OAuth2 de servicio (sin usuario interactivo).
    """

    GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"
    HEARTBEAT_INTERVAL_MINUTES = 15

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        # Credenciales de la app registrada en Azure AD
        # Nunca hardcodeadas — provienen del CredentialVault
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = None
        self._token_expires_at = None

    def _get_access_token(self) -> str:
        """Obtiene o renueva el token OAuth2 de servicio."""
        now = datetime.utcnow()
        if self._access_token and self._token_expires_at and now < self._token_expires_at:
            return self._access_token

        token_url = (
            f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        )
        response = httpx.post(token_url, data={
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://graph.microsoft.com/.default"
        })
        response.raise_for_status()

        token_data = response.json()
        self._access_token = token_data["access_token"]
        self._token_expires_at = now + timedelta(seconds=token_data["expires_in"] - 60)
        return self._access_token


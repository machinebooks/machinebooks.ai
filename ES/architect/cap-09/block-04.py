# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
# Ejemplo didáctico: cliente CRM con OAuth2 y refresco automático
# Patrón: backend/services/crm/crm_client.py
# Credenciales cargadas desde variables de entorno vía current_app.config

import requests
from datetime import datetime, timedelta
from models.crm import CRMCredentials
from utils.crypto import decrypt_value

class CRMClient:
    """Cliente HTTP para el CRM corporativo con gestión automática de tokens OAuth2."""

    def __init__(self, user_id: int):
        self.user_id = user_id
        self._credentials = None

    def _get_valid_token(self) -> str:
        """Devuelve un token válido, refrescando si es necesario."""
        creds = CRMCredentials.query.filter_by(user_id=self.user_id).first()
        if not creds:
            raise PermissionError("Usuario sin credenciales CRM configuradas")

        # Refrescar si el token expira en menos de 5 minutos
        if creds.token_expires_at < datetime.utcnow() + timedelta(minutes=5):
            self._refresh_token(creds)

        return decrypt_value(creds.access_token_encrypted)

    def _refresh_token(self, creds: CRMCredentials):
        """Solicita un nuevo token usando el refresh_token almacenado."""
        # CRM_BASE_URL, CRM_CLIENT_ID y CRM_CLIENT_SECRET: cargados
        # desde current_app.config o variables de entorno
        response = requests.post(
            f"{CRM_BASE_URL}/oauth/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": decrypt_value(creds.refresh_token_encrypted),
                "client_id": CRM_CLIENT_ID,
                "client_secret": CRM_CLIENT_SECRET,
            },
            timeout=10
        )
        response.raise_for_status()
        token_data = response.json()

        # Actualizar credenciales cifradas en base de datos
        creds.update_tokens(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", creds.refresh_token_encrypted),
            expires_in=token_data["expires_in"]
        )

    def get_cases(self, modified_since: datetime = None) -> list:
        """Recupera casos del CRM, opcionalmente filtrados por fecha de modificación."""
        token = self._get_valid_token()
        params = {}
        if modified_since:
            params["modified_since"] = modified_since.isoformat()

        response = requests.get(
            f"{CRM_BASE_URL}/api/cases",
            headers={"Authorization": f"Bearer {token}"},
            params=params,
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("cases", [])

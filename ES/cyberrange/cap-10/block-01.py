# Extraído de: LibroCyberrange/cap-10-servicios-proxmox.md
# Ejemplo didáctico: función unificada de acceso a Proxmox
# Patrón: backend/services/proxmox_sdk_service.py

from proxmoxer import ProxmoxAPI
from typing import Any, Dict, List, Optional, Tuple

def proxmox(type: str, action: str, **params) -> Dict[str, Any]:
    """
    Punto de entrada único para operar con Proxmox VE.
    Devuelve siempre: {"success": bool, "result"/"items"/"error": ...}
    """
    # — Conexión cacheada con reconexión automática —
    def _ensure(force_reconnect=False) -> Tuple[bool, Optional[ProxmoxAPI], Optional[str]]:
        # Si ya tenemos un cliente autenticado, verificar que sigue vivo
        if not force_reconnect and getattr(proxmox, "_client", None):
            try:
                _ = proxmox._client.version.get()  # Ping ligero
                return True, proxmox._client, None
            except Exception as e:
                error_msg = str(e).lower()
                if "401" in error_msg or "ticket" in error_msg:
                    # Ticket expirado: forzar reconexión
                    force_reconnect = True
                else:
                    return False, None, str(e)

        # Crear nueva conexión (por password o por API token)
        try:
            # verify_ssl configurable: True por defecto (producción).
            # Solo False en lab con certificados autofirmados.
            ssl_verify = settings.proxmox_ssl_verify  # True por defecto
            if token_id and token_secret:
                client = ProxmoxAPI(
                    host, port=port,
                    user=token_user, token_name=token_name,
                    token_value=token_secret,
                    verify_ssl=ssl_verify, timeout=60
                )
            else:
                client = ProxmoxAPI(
                    host, port=port,
                    user=user, password=password,
                    verify_ssl=ssl_verify, timeout=60
                )
            _ = client.version.get()  # Verificar que funciona
            proxmox._client = client
            return True, client, None
        except Exception as e:
            return False, None, str(e)

    ok, client, err = _ensure()
    if not ok:
        return {"success": False, "error": f"Sin conexión: {err}"}

    # — Dispatch por acción —
    # (cada acción es un bloque if/elif con su propia lógica)
    ...

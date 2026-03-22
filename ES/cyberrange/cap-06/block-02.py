# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_sdk_service.py
# Reconexión automática ante expiración de ticket

def _ensure_connection(force_reconnect: bool = False):
    """
    Verifica que la conexión al hipervisor esté activa.
    Si el ticket ha expirado, reconecta automáticamente.
    """
    if not force_reconnect and _is_authenticated():
        try:
            # Verificar que el ticket sigue siendo válido
            _ = client.version.get()
            return True, client, None
        except Exception as e:
            error_msg = str(e).lower()
            if "401" in error_msg or "ticket" in error_msg:
                logger.warning("Ticket expirado, reconectando...")
                force_reconnect = True
            else:
                return False, None, str(e)

    # Reconectar: soporta token de API o usuario/contraseña
    host = settings.proxmox_default_host
    user = settings.proxmox_default_user

    ssl_verify = settings.proxmox_ssl_verify  # True por defecto
    if settings.proxmox_token_id and settings.proxmox_token_secret:
        # Autenticación por token (no caduca)
        client = ProxmoxAPI(
            host, port=port, user=token_user,
            token_name=token_name, token_value=token_secret,
            verify_ssl=ssl_verify, timeout=60
        )
    elif settings.proxmox_default_password:
        # Autenticación por ticket (caduca en 2h)
        client = ProxmoxAPI(
            host, port=port, user=user,
            password=password,
            verify_ssl=ssl_verify, timeout=60
        )

    # Verificar conectividad
    _ = client.version.get()
    return True, client, None

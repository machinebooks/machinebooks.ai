# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
    except Exception as exc:
        logger.error(f"[{task_id}] Error en sincronización portal: {exc}")
        _update_task_status(task_id, "failed", str(exc))

        # Siguiendo el patrón de reintentos descrito en el Capítulo 8,
        # reintento automático si no es el último intento
        try:
            raise self.retry(exc=exc, countdown=60)
        except self.MaxRetriesExceededError:
            _audit_log(
                user_id=user_id,
                action="AUTOMATION_PORTAL_SYNC_FAILED",
                severity="WARNING",
                details={"task_id": task_id, "error": str(exc)}
            )
            raise


def _update_task_status(task_id: str, status: str, message: str):
    """Actualiza el estado de la tarea en Redis para que la UI pueda mostrarlo."""
    r = _get_redis_client()
    state = {"status": status, "message": message}
    r.setex(f"task:status:{task_id}", 3600, json.dumps(state))


def _get_credentials_from_vault(credential_id: str) -> dict:
    """Recupera y descifra credenciales del CredentialVault."""
    from models.credential_vault import CredentialVault
    vault_entry = CredentialVault.query.filter_by(
        identifier=credential_id,
        active=True
    ).first()
    if not vault_entry:
        raise ValueError(f"Credencial '{credential_id}' no encontrada en el vault")
    return vault_entry.decrypt()  # AES-256, nunca en claro en DB

# Extraído de: LibroCyberrange/cap-06-proxmox-virtualizacion.md
# Ejemplo didáctico: patrones/backend/services/proxmox_manager.py
# Cooldown por tipo de sincronización: 15 segundos mínimo

def _can_sync(self, sync_type: str) -> bool:
    """
    Verificar si han pasado al menos 15 segundos
    desde la última sincronización de este tipo.
    """
    last_sync = self._last_sync_timestamps.get(sync_type)
    if last_sync is None:
        return True  # Primera vez, permitir

    elapsed = (datetime.now() - last_sync).total_seconds()
    return elapsed >= self._sync_cooldown_seconds  # 15 segundos

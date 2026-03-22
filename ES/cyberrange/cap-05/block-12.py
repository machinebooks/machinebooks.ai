# Extraído de: LibroCyberrange/cap-05-arquitectura.md
# Ejemplo didáctico: patrones/backend/config.py
# Configuración centralizada con Pydantic

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base de datos
    database_url: str = "mysql+pymysql://user:pass@localhost:3306/cyberrange"

    # JWT
    jwt_secret: str = ""                # Obligatorio: RuntimeError si no se configura
    jwt_exp_hours: int = 4

    # Proxmox
    proxmox_default_host: str = "proxmox.local"
    proxmox_default_port: int = 8006
    proxmox_default_user: str = "cyberrange@pve"
    proxmox_token_id: str = ""          # Obligatorio: RuntimeError si no se configura
    proxmox_token_secret: str = ""      # Obligatorio: RuntimeError si no se configura
    proxmox_ssl_verify: bool = True     # False solo en lab con cert autofirmado

    # Sincronización
    proxmox_sync_interval_minutes: int = 15
    proxmox_auto_cleanup_snapshots: bool = True
    proxmox_snapshot_retention_days: int = 7

    # Pool management
    proxmox_default_pool_prefix: str = "cyberrange"

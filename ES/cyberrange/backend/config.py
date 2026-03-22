# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/config.py — Configuración centralizada
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
    proxmox_sync_interval_minutes: int = 15

    # Seguridad
    password_min_length: int = 12
    max_failed_logins: int = 5
    account_lockout_minutes: int = 30
    session_timeout_minutes: int = 60

    # Workzones
    max_workzones: int = 16
    workzone_network_base: str = "10.0.0.0/8"
    vlan_range_start: int = 100
    vlan_range_end: int = 999

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

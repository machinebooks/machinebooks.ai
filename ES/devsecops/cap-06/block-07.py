# Extraído de: LibroDevSecOps/cap-06-secretos.md
import hvac
import os

def get_database_credentials() -> dict:
    """Solicita credenciales efímeras de base de datos a Vault."""
    client = hvac.Client(
        url=os.environ["VAULT_ADDR"],
        token=os.environ["VAULT_TOKEN"],
    )

    # Solicitar credenciales dinámicas con TTL de 1 hora
    response = client.secrets.database.generate_credentials(
        name="mi-app-readonly",  # Rol predefinido en Vault
        mount_point="database",
    )

    return {
        "username": response["data"]["username"],
        "password": response["data"]["password"],
        "lease_id": response["lease_id"],
        "lease_duration": response["lease_duration"],  # 3600 segundos
    }

def renew_lease(lease_id: str) -> None:
    """Renueva el lease antes de que expire."""
    client = hvac.Client(
        url=os.environ["VAULT_ADDR"],
        token=os.environ["VAULT_TOKEN"],
    )
    client.sys.renew_lease(lease_id=lease_id, increment=3600)

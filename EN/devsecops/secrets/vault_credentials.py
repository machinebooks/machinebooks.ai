# Source: The DevSecOps and the Machine -- Chapter 6
# Pattern: HashiCorp Vault ephemeral credentials

import hvac
import os

def get_database_credentials() -> dict:
    """Request ephemeral database credentials from Vault."""
    client = hvac.Client(
        url=os.environ["VAULT_ADDR"],
        token=os.environ["VAULT_TOKEN"],
    )

    # Request dynamic credentials with 1-hour TTL
    response = client.secrets.database.generate_credentials(
        name="my-app-readonly",  # Predefined role in Vault
        mount_point="database",
    )

    return {
        "username": response["data"]["username"],
        "password": response["data"]["password"],
        "lease_id": response["lease_id"],
        "lease_duration": response["lease_duration"],  # 3600 seconds
    }

def renew_lease(lease_id: str) -> None:
    """Renew the lease before it expires."""
    client = hvac.Client(
        url=os.environ["VAULT_ADDR"],
        token=os.environ["VAULT_TOKEN"],
    )
    client.sys.renew_lease(lease_id=lease_id, increment=3600)
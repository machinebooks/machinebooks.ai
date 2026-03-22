# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
from google.cloud import billing_v1

client = billing_v1.CloudBillingClient()

# Listar cuentas de billing accesibles
accounts = client.list_billing_accounts()
for account in accounts:
    print(f"Cuenta: {account.display_name}")
    print(f"  ID: {account.name}")
    print(f"  Abierta: {account.open}")

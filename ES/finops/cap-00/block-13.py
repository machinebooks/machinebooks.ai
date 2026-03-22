# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
from google.cloud import billing_v1
from google.oauth2 import service_account

# Opción 1: Service account (producción)
credentials = service_account.Credentials.from_service_account_file(
    "path/to/service-account.json",
    scopes=["https://www.googleapis.com/auth/cloud-billing"]
)

# Opción 2: Application Default Credentials (desarrollo)
# Ejecutar: gcloud auth application-default login
client = billing_v1.CloudBillingClient(credentials=credentials)

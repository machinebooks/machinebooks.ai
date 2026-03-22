# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
from azure.identity import DefaultAzureCredential
from azure.mgmt.costmanagement import CostManagementClient

# DefaultAzureCredential intenta, en orden:
#   1. Variables de entorno (AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET)
#   2. Managed Identity (en Azure)
#   3. Azure CLI login (en desarrollo)
credential = DefaultAzureCredential()
client = CostManagementClient(credential)

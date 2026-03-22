# Source: The FinOps Engineer and the Machine -- Appendix B
# Pattern: GCP Cloud Billing API examples

from google.cloud import billing_v1
from google.oauth2 import service_account

# Option 1: Service account (production)
credentials = service_account.Credentials.from_service_account_file(
    "path/to/service-account.json",
    scopes=["https://www.googleapis.com/auth/cloud-billing"]
)

# Option 2: Application Default Credentials (development)
# Run: gcloud auth application-default login
client = billing_v1.CloudBillingClient(credentials=credentials)

from google.cloud import billing_v1

client = billing_v1.CloudBillingClient()

# List accessible billing accounts
accounts = client.list_billing_accounts()
for account in accounts:
    print(f"Account: {account.display_name}")
    print(f"  ID: {account.name}")
    print(f"  Open: {account.open}")

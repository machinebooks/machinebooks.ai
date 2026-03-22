# Extraído de: LibroFinOps/apendice-b-apis-coste-cloud.md
from azure.mgmt.advisor import AdvisorManagementClient

advisor = AdvisorManagementClient(credential, "<TU_SUBSCRIPTION_ID>")

recommendations = advisor.recommendations.list(
    filter="Category eq 'Cost'"
)

for rec in recommendations:
    print(f"Recurso: {rec.resource_metadata.resource_id}")
    print(f"  Impacto: {rec.impact}")
    print(f"  Recomendación: {rec.short_description.solution}")
    print(f"  Ahorro estimado: {rec.extended_properties.get('annualSavingsAmount', 'N/A')}")

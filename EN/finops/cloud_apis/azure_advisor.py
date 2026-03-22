# Source: The FinOps Engineer and the Machine -- Appendix B
# Pattern: Azure Advisor cost recommendations

from azure.mgmt.advisor import AdvisorManagementClient

advisor = AdvisorManagementClient(credential, "<YOUR_SUBSCRIPTION_ID>")

recommendations = advisor.recommendations.list(
    filter="Category eq 'Cost'"
)

for rec in recommendations:
    print(f"Resource: {rec.resource_metadata.resource_id}")
    print(f"  Impact: {rec.impact}")
    print(f"  Recommendation: {rec.short_description.solution}")
    print(f"  Estimated savings: {rec.extended_properties.get('annualSavingsAmount', 'N/A')}")

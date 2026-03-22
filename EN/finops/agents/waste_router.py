# Source: The FinOps Engineer and the Machine -- Chapter 15
# Pattern: FastAPI routes for waste management

# api/routes/waste.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/waste", tags=["Waste Cleanup"])


@router.get("/scan")
async def get_waste_scan():
    """
    Executes a complete orphaned resource scan and returns the cleanup
    proposal. Resources are classified by risk and grouped to
    facilitate approval.
    """
    # Scan all resource types
    volumes = scan_unattached_ebs_volumes()
    eips = scan_unused_elastic_ips()
    lbs = scan_empty_load_balancers()
    all_resources = volumes + eips + lbs

    if not all_resources:
        return {'message': 'No orphaned resources found', 'resources': []}

    # Classify risk with Claude
    classifications = classify_waste_risk(all_resources)

    # Combine scan data with risk classification
    resource_map = {r['resource_id']: r for r in all_resources}
    classified_resources = []
    total_potential_savings = 0.0

    for classification in classifications:
        resource = resource_map.get(classification['resource_id'], {})
        combined = {**resource, **classification}
        classified_resources.append(combined)

        if classification['risk_level'] == 'low':
            total_potential_savings += resource.get('monthly_cost_usd', 0)

    # Group by risk level
    by_risk = {
        'low': [r for r in classified_resources if r.get('risk_level') == 'low'],
        'medium': [r for r in classified_resources if r.get('risk_level') == 'medium'],
        'high': [r for r in classified_resources if r.get('risk_level') == 'high']
    }

    return {
        'total_resources': len(classified_resources),
        'total_monthly_waste_usd': sum(
            r.get('monthly_cost_usd', 0) for r in all_resources
        ),
        'safe_cleanup_monthly_savings_usd': round(total_potential_savings, 2),
        'by_risk': by_risk,
        'message': (
            f"Found {len(by_risk['low'])} low-risk resources "
            f"that can be safely deleted, with potential savings of "
            f"${total_potential_savings:.2f}/month"
        )
    }

# Extraído de: LibroFinOps/cap-15-waste-automatico.md
# api/routes/waste.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/waste", tags=["Waste Cleanup"])


@router.get("/scan")
async def get_waste_scan():
    """
    Ejecuta un escaneo completo de recursos huérfanos y devuelve la propuesta
    de cleanup. Los recursos se clasifican por riesgo y se agrupan para
    facilitar la aprobación.
    """
    # Escaneamos todos los tipos de recursos
    volumes = scan_unattached_ebs_volumes()
    eips = scan_unused_elastic_ips()
    lbs = scan_empty_load_balancers()
    all_resources = volumes + eips + lbs

    if not all_resources:
        return {'message': 'No se encontraron recursos huérfanos', 'resources': []}

    # Clasificamos el riesgo con Claude
    classifications = classify_waste_risk(all_resources)

    # Combinamos los datos de escaneo con la clasificación de riesgo
    resource_map = {r['resource_id']: r for r in all_resources}
    classified_resources = []
    total_potential_savings = 0.0

    for classification in classifications:
        resource = resource_map.get(classification['resource_id'], {})
        combined = {**resource, **classification}
        classified_resources.append(combined)

        if classification['risk_level'] == 'low':
            total_potential_savings += resource.get('monthly_cost_usd', 0)

    # Agrupamos por nivel de riesgo
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
            f"Se encontraron {len(by_risk['low'])} recursos de riesgo bajo "
            f"que pueden eliminarse con seguridad, con un ahorro potencial de "
            f"${total_potential_savings:.2f}/mes"
        )
    }

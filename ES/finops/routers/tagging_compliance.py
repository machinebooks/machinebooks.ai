# Extraído de: LibroFinOps/cap-05-tagging-cloud.md
# routers/tagging_compliance.py
from fastapi import APIRouter
import boto3

router = APIRouter(prefix="/api/tagging", tags=["Tagging Compliance"])

REQUIRED_TAGS = ["environment", "team", "service", "cost-center"]

@router.get("/compliance-summary")
async def get_tagging_compliance(region: str = "eu-west-1"):
    """
    Devuelve el porcentaje de recursos correctamente etiquetados
    por tipo de recurso en la región indicada.
    """
    ec2 = boto3.client("ec2", region_name=region)

    instances = []
    paginator = ec2.get_paginator("describe_instances")
    for page in paginator.paginate():
        for r in page["Reservations"]:
            for i in r["Instances"]:
                if i["State"]["Name"] != "terminated":
                    instances.append(i)

    total = len(instances)
    if total == 0:
        return {"total": 0, "compliant": 0, "compliance_pct": 100.0}

    compliant = 0
    for instance in instances:
        current_tags = {t["Key"] for t in instance.get("Tags", [])}
        if all(tag in current_tags for tag in REQUIRED_TAGS):
            compliant += 1

    return {
        "region": region,
        "resource_type": "EC2",
        "total": total,
        "compliant": compliant,
        "non_compliant": total - compliant,
        "compliance_pct": round((compliant / total) * 100, 1),
        "required_tags": REQUIRED_TAGS,
    }

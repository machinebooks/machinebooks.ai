# Extraído de: LibroFinOps/cap-05-tagging-cloud.md
# tasks/apply_tag_corrections.py
import boto3

def apply_approved_tag_corrections(proposal_ids: list[str]) -> dict:
    """
    Aplica las correcciones de tags aprobadas por el equipo de FinOps.
    Solo procesa propuestas en estado 'approved'.
    Registra el resultado de cada aplicación.
    """
    ec2 = boto3.client("ec2", region_name="eu-west-1")
    results = {"applied": [], "failed": []}

    for proposal_id in proposal_ids:
        # Cargar la propuesta aprobada desde base de datos
        proposal = load_proposal(proposal_id)
        if proposal["status"] != "approved":
            continue

        try:
            if proposal["resource_type"] == "EC2":
                ec2.create_tags(
                    Resources=[proposal["resource_id"]],
                    Tags=[
                        {"Key": k, "Value": v}
                        for k, v in proposal["proposed_tags"].items()
                    ],
                )
                update_proposal_status(proposal_id, "applied")
                results["applied"].append(proposal_id)
        except Exception as exc:
            update_proposal_status(proposal_id, "failed", error=str(exc))
            results["failed"].append({"id": proposal_id, "error": str(exc)})

    return results

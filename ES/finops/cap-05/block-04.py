# Extraído de: LibroFinOps/cap-05-tagging-cloud.md
def list_untagged_ec2(region: str, required_tags: list[str]) -> list[dict]:
    """
    Consulta AWS y devuelve instancias EC2 con etiquetas incompletas.
    """
    ec2 = boto3.client("ec2", region_name=region)
    response = ec2.describe_instances()

    untagged = []
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            # Construir dict de etiquetas actuales
            current_tags = {
                t["Key"]: t["Value"]
                for t in instance.get("Tags", [])
            }
            missing = [t for t in required_tags if t not in current_tags]

            if missing:
                untagged.append({
                    "instance_id": instance["InstanceId"],
                    "name": current_tags.get("Name", "sin nombre"),
                    "instance_type": instance["InstanceType"],
                    "state": instance["State"]["Name"],
                    "vpc_id": instance.get("VpcId", ""),
                    "launch_time": instance["LaunchTime"].isoformat(),
                    "current_tags": current_tags,
                    "missing_tags": missing,
                })

    return untagged


def propose_tag_correction(
    resource_id: str,
    resource_type: str,
    proposed_tags: dict,
    reasoning: str,
    confidence: str,
) -> dict:
    """
    Registra la propuesta en base de datos para revisión humana.
    Devuelve el ID de la propuesta creada.
    """
    proposal = {
        "id": f"prop-{resource_id}-{int(datetime.now(timezone.utc).timestamp())}",
        "resource_id": resource_id,
        "resource_type": resource_type,
        "proposed_tags": proposed_tags,
        "reasoning": reasoning,
        "confidence": confidence,
        "status": "pending_review",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    # En producción: persistir en base de datos
    # await session.add(TagCorrectionProposal(**proposal))
    return {"proposal_id": proposal["id"], "status": "registered"}
